# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

## [0.1.5] - 08.15.2025

### Changed

- Set python compatibility to >=3.11 <3.13

### Added

- Created method in ImagePreprocessor to preprocess images based on a preprocessing result

## [0.1.4] - 07.15.2025

### Added

- Added a cropping padding to significantly improve dart detection accuracy
- Introduced new services for calibration and scoring

### Changed

- Refactored calibration and scoring service for reusability and maintainability

## [0.1.3] - 06.15.2025

### Improved

- Enhanced performance and usability of `dart-image-scorer` and `dart-calibration-visualizer` scripts
- Improved calibration point detection accuracy and stability
- Added more robust error handling for calibration point processing

## [0.1.2] - 06.07.2025

### Fixed

- Fixed the two scripts `dart-image-scorer` and `dart-calibration-visualizer` by moving them to the `dart_detection`
  package
  directory

## [0.1.1] - 06.06.2025

### Added

- Initial release of dart-detection package
- Dart detection using YOLO models
- Dartboard detection and cropping functionality
- Scoring system for detected darts
- Image preprocessing capabilities
- CLI tools: `dart-image-scorer` and `dart-calibration-visualizer`