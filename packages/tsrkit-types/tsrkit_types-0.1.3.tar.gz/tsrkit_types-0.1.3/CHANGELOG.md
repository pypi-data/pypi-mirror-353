# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-06-03

### Added
- Initial release of tsrkit-types library
- Core `Codable` interface for all types
- Integer types: `Uint` with fixed-size (`U8`, `U16`, `U32`, `U64`) and variable-size variants
- String type: `String` with UTF-8 encoding and length prefix
- Boolean type: `Bool` with single-byte encoding
- Null types: `Null` singleton and `Nullable[T]` wrapper
- Choice types: `Choice[T1, T2, ...]` for tagged unions and `Option[T]` for optional values
- Container types:
  - Sequence types: `Array`, `Vector`, `TypedArray`, `TypedVector`, `BoundedVector`, `TypedBoundedVector`
  - Dictionary type: `Dictionary[K, V]` with typed keys and values
- Bytes types: `Bytes` for raw binary data and `BitArray` for bit sequences
- Enumeration type: `Enum` with integer backing and string names
- Structured types: `@structure` decorator for automatic `Codable` implementation
- Binary serialization with efficient encoding formats
- JSON serialization with customizable field mapping
- Type safety with runtime validation
- Generic type parameters for flexible usage
- Comprehensive test suite
- MIT license
- Complete API documentation

### Features
- All types implement the `Codable` interface for consistent encoding/decoding
- Memory-efficient encoding optimized for common use cases
- Type validation at construction and assignment time
- Support for nested and complex type compositions
- Zero-dependency core library
- Python 3.11+ support

## [0.1.3] - 2025-01-03

### Fixed
- **Option JSON handling**: Fixed `Option.from_json()` to properly handle `None` values by creating empty Options
- **Choice serialization**: Improved `Choice.encode_into()` to correctly identify choice variants using both key and type matching, fixing issues with duplicate keys (like in Option types)
- **Struct None handling**: Enhanced `struct.from_json()` to properly handle `None` values for Option and NullType fields without requiring explicit defaults

### Added
- **Option JSON methods**: Added dedicated `to_json()` and `from_json()` methods to Option class for cleaner JSON serialization
- **Improved type hints**: Enhanced struct decorator to provide better IDE support and type hints for Codable interface methods

### Changed
- **Choice from_json**: Simplified Choice.from_json() by moving Option-specific logic to Option class
- **Serialization robustness**: Made Choice encoding more reliable for complex type hierarchies

## [Unreleased]

### Planned
- Performance optimizations for large data structures
- Additional integer types (signed integers)
- Time and date types
- UUID type
- Decimal/fixed-point numeric types
- Schema validation and migration support
- Code generation tools
- Benchmarking suite
- Documentation examples and tutorials 