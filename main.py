import os
import sys
import pandas as pd
from typing import Dict, Tuple
import config
from scraper.codeforces import CodeforcesScraper
from sheets.operations import clean_google_sheets
from utils.logger import logger


def load_existing_csvs() -> Dict[str, pd.DataFrame]:
    """
    Load existing CSV files instead of scraping

    Returns:
        Dictionary mapping contest name to DataFrame
    """
    dfs = {}

    for contest_config in config.CONTESTS:
        contest_name = contest_config[0]
        csv_file = f"{contest_name}_standings.csv"

        if not os.path.exists(csv_file):
            logger.error(
                f"❌ ERROR: {csv_file} not found. Set RUN_SCRAPER=True in .env"
            )
            sys.exit(1)

        logger.info(f"📂 Loading existing CSV: {csv_file}")
        df = pd.read_csv(csv_file)
        dfs[contest_name] = df
        logger.info(f"✅ Loaded {len(df)} participants\n")

    return dfs


def generate_combined_csv(dfs: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Generate combined CSV with totals across all contests

    Args:
        dfs: Dictionary mapping contest name to DataFrame

    Returns:
        Combined DataFrame
    """
    logger.info("\n" + "=" * 60)
    logger.info("STEP 4: GENERATING COMBINED RESULTS")
    logger.info("=" * 60)

    # Collect all unique handles
    all_handles = set()
    for df in dfs.values():
        all_handles.update(df["Handle"].tolist())

    combined_data = []

    for handle in sorted(all_handles):
        row = {"Handle": handle}
        total_all_contests = 0

        for contest_config in config.CONTESTS:
            contest_name = contest_config[0]
            df = dfs[contest_name]
            match = df[df["Handle"] == handle]

            if not match.empty:
                solved = match.iloc[0]["Total_Solved"]
            else:
                solved = 0

            row[f"{contest_name}_Solved"] = solved
            total_all_contests += solved

        row["Total_All_Contests"] = total_all_contests
        combined_data.append(row)

    # Create DataFrame and sort
    combined_df = pd.DataFrame(combined_data)
    combined_df = combined_df.sort_values(
        "Total_All_Contests", ascending=False
    ).reset_index(drop=True)

    # Save to CSV
    combined_df.to_csv(config.COMBINED_CSV, index=False, encoding="utf-8-sig")

    logger.info(f"\n✅ Generated combined results CSV: {config.COMBINED_CSV}")
    logger.info(f"✅ Total unique participants: {len(combined_df)}\n")

    return combined_df


def print_summary():
    """Print automation summary"""
    logger.info("\n" + "=" * 60)
    logger.info("ACM AUTOMATION (Multi-Contest)")
    logger.info("=" * 60)
    logger.info(f"Number of contests: {len(config.CONTESTS)}")

    for contest_config in config.CONTESTS:
        name = contest_config[0]
        threshold = contest_config[2] if len(contest_config) > 2 else None

        if threshold is not None:
            logger.info(f"  - {name} (Individual Threshold: {threshold})")
        else:
            logger.info(f"  - {name} (No Individual Threshold)")

    logger.info(f"\nGlobal Threshold: {config.GLOBAL_THRESHOLD}")
    logger.info("=" * 60 + "\n")


def main():
    """Main execution function"""
    try:
        if not config.validate_config():
            logger.error(
                "Configuration validation failed. Please check your .env file."
            )
            sys.exit(1)

        print_summary()

        if config.RUN_SCRAPER:
            results = CodeforcesScraper.scrape_all_contests()
            dfs = {contest_name: df for contest_name, (df, _) in results.items()}
        else:
            dfs = load_existing_csvs()

        clean_google_sheets(dfs)

        generate_combined_csv(dfs)

        logger.info("\n" + "=" * 60)
        logger.info("🎉 AUTOMATION COMPLETE!")
        logger.info("=" * 60)
        logger.info(f"Check {config.COMBINED_CSV} for full results.\n")

    except KeyboardInterrupt:
        logger.warning("\n⚠️  Process interrupted by user")
        sys.exit(0)

    except Exception as e:
        logger.error(f"\n❌ Fatal error: {e}")
        logger.exception("Full traceback:")
        sys.exit(1)


if __name__ == "__main__":
    main()
