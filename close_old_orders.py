#!/usr/bin/env python3
import logging
from database import update_completed_orders


def main():
    try:
        updated_count = update_completed_orders()
        logging.info(f"Updated orders: {updated_count}")
    except Exception as e:
        logging.error(f"Error when closing old orders: {e}")


if __name__ == "__main__":
    main()
