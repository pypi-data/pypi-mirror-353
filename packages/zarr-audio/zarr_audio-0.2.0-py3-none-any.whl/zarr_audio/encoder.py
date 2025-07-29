import os
import shutil
import tempfile
import warnings
from typing import Optional, Tuple

import fsspec
import numpy as np
import soundfile as sf
import zarr
from flac_numcodecs import Flac


class AudioEncoder:
    VALID_S3_STORAGE_CLASSES = {
        "STANDARD",
        "STANDARD_IA",
        "ONEZONE_IA",
        "INTELLIGENT_TIERING",
        "GLACIER",
        "DEEP_ARCHIVE",
        "REDUCED_REDUNDANCY",
    }

    def __init__(
        self,
        input_uri: str,
        output_uri: str,
        storage_options: Optional[dict] = None,
        chunk_duration: int = 10,
        encoding_read_duration: int = 600,
        storage_class: Optional[str] = None,
    ):
        """
        Initialize an AudioEncoder.

        Args:
            input_uri: fsspec URI to the source audio file.
            output_uri: fsspec URI to the output Zarr group.
            storage_options: Dictionary of options passed to fsspec.
            chunk_duration: Duration (sec) of each Zarr chunk.
            encoding_read_duration: Duration (sec) of read blocks while encoding; only adjust if OOM errors occur during encoding.
            storage_class: Optional S3 storage class (e.g., 'INTELLIGENT_TIERING'). Defaults to INTELLIGENT_TIERING.
        """
        self.input_uri = input_uri
        self.output_uri = output_uri
        self.storage_options = storage_options or {}
        self.chunk_duration = chunk_duration
        self.encoding_read_duration = encoding_read_duration
        self._local_path: Optional[str] = None

        self.storage_class = storage_class

        if self.output_uri.startswith("s3://"):
            sc = self.storage_class or "INTELLIGENT_TIERING"

            if sc not in self.VALID_S3_STORAGE_CLASSES:
                raise ValueError(
                    f"Invalid S3 storage class: '{sc}'. "
                    f"Must be one of {sorted(self.VALID_S3_STORAGE_CLASSES)}"
                )

            self.storage_options.setdefault("s3_additional_kwargs", {})[
                "StorageClass"
            ] = sc

    def _detect_dtype_and_bit_depth(self, subtype: str) -> Tuple[str, int]:
        """
        Determine the appropriate NumPy dtype and bit depth based on audio subtype.

        For PCM_32, performs probing of the first frame to distinguish float-style content.

        Args:
            subtype: The audio subtype string from soundfile.

        Returns:
            A tuple (dtype, bit_depth) where dtype is a NumPy dtype string and bit_depth is an int.
        """
        subtype_to_dtype = {
            "PCM_16": ("int16", 16),
            "PCM_24": ("int32", 24),
            "FLOAT": ("float32", 32),
            "DOUBLE": ("float64", 64),
        }

        if subtype == "PCM_32":
            with sf.SoundFile(self._local_path) as sf_info:
                sf_info.seek(0)
                probe = sf_info.read(frames=1, dtype="int32", always_2d=True)
                sample = probe[0, 0]
                if abs(sample) < 2**24:
                    print(
                        "🔎 Detected float32-style content in PCM_32. Treating as float32."
                    )
                    return "float32", 32
                else:
                    print("🔎 Detected true int32 PCM_32 content.")
                    return "int32", 32

        return subtype_to_dtype.get(subtype, ("int16", 16))

    def encode(self) -> str:
        """
        Perform encoding from input_uri to output_uri as a Zarr container.

        The audio is read in large blocks from a local temporary copy of the input file
        and written to Zarr chunks using the configured compressor.

        Returns:
            The output_uri to the completed Zarr store.
        """
        with tempfile.NamedTemporaryFile(delete=False, suffix=".audio") as tmp:
            self._local_path = tmp.name
            with fsspec.open(self.input_uri, **self.storage_options) as f_in:
                shutil.copyfileobj(f_in, tmp)

        try:
            with sf.SoundFile(self._local_path) as sf_info:
                samplerate = sf_info.samplerate
                channels = sf_info.channels
                subtype = sf_info.subtype
                frames = sf_info.frames
                duration_sec = frames / samplerate

            dtype, bit_depth = self._detect_dtype_and_bit_depth(subtype)
            chunk_size = int(samplerate * self.chunk_duration)

            if dtype == "int16":
                compressor = Flac(level=8)
                compression = "flac"
            else:
                warnings.warn(
                    f"⚠️ Falling back to Blosc compression for unsupported dtype {dtype}"
                )
                compressor = zarr.Blosc(cname="zstd", clevel=5, shuffle=1)
                compression = "blosc"

            store = fsspec.get_mapper(self.output_uri, **self.storage_options)
            root = zarr.open_group(store, mode="w")

            audio_array = root.create_dataset(
                "audio",
                shape=(channels, frames),
                chunks=(channels, chunk_size),
                dtype=dtype,
                compressor=compressor,
                overwrite=True,
            )

            read_block_size = int(samplerate * self.encoding_read_duration)

            with sf.SoundFile(self._local_path) as sf_info:
                start_sample = 0
                while start_sample < frames:
                    sf_info.seek(start_sample)
                    n_to_read = min(read_block_size, frames - start_sample)
                    block = sf_info.read(n_to_read, dtype=dtype, always_2d=True)
                    block = block.T  # shape: (channels, samples)
                    audio_array[:, start_sample : start_sample + block.shape[1]] = block
                    start_sample += block.shape[1]
                    del block

            compression_ratio = None
            try:
                if self.output_uri.startswith("file://"):

                    def get_dir_size(path: str) -> int:
                        total = 0
                        for dirpath, _, filenames in os.walk(path):
                            for f in filenames:
                                fp = os.path.join(dirpath, f)
                                total += os.path.getsize(fp)
                        return total

                    local_path = self.output_uri.replace("file://", "")
                    compressed_bytes = get_dir_size(local_path)
                    uncompressed_bytes = audio_array.nbytes
                    if compressed_bytes:
                        compression_ratio = uncompressed_bytes / compressed_bytes
                else:
                    warnings.warn("Compression ratio only supported for file:// URIs.")
            except Exception as e:
                warnings.warn(f"Could not compute compression ratio: {e}")

            root.attrs.update(
                {
                    "samplerate": samplerate,
                    "channels": channels,
                    "samples": frames,
                    "bit_depth": bit_depth,
                    "dtype": str(np.dtype(dtype)),
                    "compression": compression,
                    "compression_ratio": compression_ratio,
                    "original_uri": self.input_uri,
                }
            )

            print(
                f"✅ Encoded {self.input_uri} → {self.output_uri} "
                f"[{frames / samplerate:.2f} sec, {bit_depth}-bit {dtype}, "
                f"{compression}, ratio: {compression_ratio}]"
            )

            return self.output_uri

        finally:
            print(f"🗑️ Clean-up {self._local_path}")
            os.remove(self._local_path)
