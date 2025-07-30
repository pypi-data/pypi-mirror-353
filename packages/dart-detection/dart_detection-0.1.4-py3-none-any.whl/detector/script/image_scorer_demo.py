"""Demo running dart detection with an image scorer."""

import argparse
import logging
from pathlib import Path
from typing import TYPE_CHECKING

from detector.entrypoint.image_score_pipeline import DartBoardImageToScorePipeline
from detector.model.configuration import ProcessingConfig

if TYPE_CHECKING:
    from detector.model.detection_models import DetectionResult

logger = logging.getLogger("DartImageScorerDemo")


def setup_logging() -> None:  # noqa: D103
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def main() -> None:
    """Run the Dart Detection demo with a single image."""
    parser = argparse.ArgumentParser(description="Run Dart Detection with an image scorer.")
    parser.add_argument("image_path", type=str, help="Path to the image file for dart detection")
    parser.add_argument("--config_path", type=str, default=None, help="Path to JSON config file for dart detection")
    args = parser.parse_args()
    image_path = Path(args.image_path)
    config_path = Path(args.config_path) if args.config_path else None

    setup_logging()
    detector = DartBoardImageToScorePipeline(ProcessingConfig.from_json(config_path) if config_path else None)
    result: DetectionResult = detector.detect_darts(image_path)
    if not result:
        logger.error("❌ No result returned from the detection service.")
        return
    if result.success:
        logger.info("🎯 Dart Detection Results")
        logger.info("⏱️  Processing time: %.2fs", result.processing_time)
        logger.info("-" * 50)

        if result.scoring_result:
            logger.info("🎯 Darts detected: %d", len(result.scoring_result.dart_detections))

            total_score = 0
            for i, detection in enumerate(result.scoring_result.dart_detections):
                if detection.dart_score:
                    pos = detection.transformed_position or detection.original_position
                    logger.info(
                        "  🎯 Dart %d: %s (%d pts) at (%.2f, %.2f) [Confidence: %.1f%%]",
                        i + 1,
                        detection.dart_score.score_string,
                        detection.dart_score.score_value,
                        pos.x,
                        pos.y,
                        detection.confidence * 100,
                    )
                    total_score += detection.dart_score.score_value
                else:
                    pos = detection.transformed_position or detection.original_position
                    logger.info(
                        "  ❓ Dart %d: Score pending at (%.2f, %.2f) [Confidence: %.1f%%]", i + 1, pos.x, pos.y, detection.confidence * 100
                    )

            logger.info("-" * 50)
            logger.info("🏆 Total Score: %d points", total_score)
        else:
            logger.info("❌ No darts detected")

        if result.calibration_result.calibration_points:  # type: ignore
            logger.info("🔧 Calibration points detected: %d", len(result.calibration_result.calibration_points))  # type: ignore

    else:
        error_msg = result.result_code.message
        logger.error("❌ Dart detection failed: %s", error_msg)
        if result.message:
            logger.error("   Details: %s", result.message)


if __name__ == "__main__":
    main()
