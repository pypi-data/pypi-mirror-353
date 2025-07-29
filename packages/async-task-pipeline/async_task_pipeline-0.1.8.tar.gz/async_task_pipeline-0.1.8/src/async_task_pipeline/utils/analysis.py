"""
Performance analysis utilities for async task pipeline
"""

from typing import TYPE_CHECKING

from .logging import logger

if TYPE_CHECKING:
    from ..base.pipeline import AsyncTaskPipeline


def log_pipeline_performance_analysis(pipeline: "AsyncTaskPipeline") -> None:
    """
    Log comprehensive performance analysis for an AsyncTaskPipeline.

    This function provides detailed performance metrics including:
    - Overall pipeline efficiency metrics
    - Per-stage performance breakdown with timing details
    - Individual item analysis for the first few processed items

    Args:
        pipeline: The AsyncTaskPipeline instance to analyze
    """
    if not pipeline.enable_timing:
        logger.info("Pipeline timing is disabled. No analysis available.")
        return

    logger.info("Enhanced Pipeline Performance Analysis:")
    summary = pipeline.get_latency_summary()
    logger.info(f"Total items processed: {summary['total_items']}")
    logger.info(f"Average end-to-end latency: {summary['avg_total_latency']:.3f}s")

    efficiency = summary["overall_efficiency"]
    logger.info("Overall Efficiency Metrics:")
    logger.info(f"  Computation efficiency: {efficiency['computation_efficiency']:.1%}")
    logger.info(f"  Overhead ratio: {efficiency['overhead_ratio']:.1%}")

    logger.info("Per-Stage Performance Breakdown:")
    for stage_name, stats in summary["stage_statistics"].items():
        timing = stats["timing_breakdown"]
        logger.info(f"  {stage_name}:")
        logger.info(f"    Processed: {stats['processed_count']} items")
        logger.info(f"    Avg computation time: {timing['avg_computation_time'] * 1000:.2f}ms")
        logger.info(f"    Avg queue wait time: {timing['avg_queue_wait_time'] * 1000:.2f}ms")
        logger.info(f"    Avg transmission time: {timing['avg_transmission_time'] * 1000:.2f}ms")
        logger.info(f"    Computation ratio: {timing['computation_ratio']:.1%}")

    logger.info("Detailed Analysis for First Few Items:")
    for item in pipeline.completed_items[:3]:
        breakdown = item.get_timing_breakdown()
        logger.info(f" Item {item.seq_num}:")

        if breakdown is not None and "totals" in breakdown:
            totals = breakdown["totals"]
            logger.info(f"  Total latency: {totals['total_latency'] * 1000:.2f}ms")
            logger.info(f"  Actual computation time: {totals['total_computation_time'] * 1000:.2f}ms")
            logger.info(f"  Actual overhead time: {totals['total_overhead_time'] * 1000:.2f}ms")
            logger.info(f"  Computation ratio: {totals['computation_ratio']:.1%}")
