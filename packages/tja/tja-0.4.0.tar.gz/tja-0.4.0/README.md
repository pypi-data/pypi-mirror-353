# tja-rs

An efficient TJA file parser, written in Rust, that supports Rust, Python, and WebAssembly environments.

It is highly optimized for speed and includes features such as a synthesizer for synthesizing music along with don/ka sound effects from a TJA file.

It's fast! (Parse thousands of TJAs in less than 1 second) [Check out the benchmark](https://jacoblincool.github.io/tja-rs/report/).

You can also use different parsing modes (e.g. metadata-only or metadata-and-header mode) to make it even faster.

## Building Instructions

### Rust

The Rust target requires no additional feature flags.

To build the library, run:

```sh
cargo build
```

To build the CLI tool, run:

```sh
cargo build --bin tja
```

### Python

We use `maturin` to build the Python package. The Python package requires the `python` feature flag to be enabled.

To build the Python package `.whl`, run:

```sh
maturin build -F python --release
```

To develop and test, run:

```sh
maturin develop -F python
```

> Python virtual environment is necessary. (e.g. `conda`, `micromamba`, `poetry`, `pixi`)

> To navigate variable, please check [tja.pyi](./tja.pyi)

### WebAssembly

We use `wasm-pack` to build the WebAssembly package. The WebAssembly package requires the `wasm` feature flag to be enabled.

To build the WebAssembly package, run:

```sh
wasm-pack build --features wasm
```

## Performance Benchmarks

The parser is highly optimized for performance.

It can parse a typical TJA file in under 1 ms in full mode, and in metadata-only mode in under 5 µs.

For detailed benchmarks and comparisons, check out our [benchmark report](https://jacoblincool.github.io/tja-rs/report/).

To run the benchmark:

```sh
cargo bench
```

## Synthesizer

The TJA parser includes a synthesizer binary that can synthesize music along with don/ka sound effects from a TJA file:

```sh
cargo run -F audio --bin synthesize <TJA file> <music file> <don sound file> <ka sound file> --course <course> --branch <branch>
```
