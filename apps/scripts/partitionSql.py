from datetime import datetime, timedelta

def generate_partition_and_indices_sql(timestamp_str: str) -> str:
    dt = datetime.fromisoformat(timestamp_str)
    start_date = dt.date()
    
    end_date = start_date + timedelta(days=1)
    
    table_suffix = f"{start_date.year}_{start_date.month}_{start_date.day}"
    
    create_table_sql = (
        f"CREATE TABLE IF NOT EXISTS course_completion_events_{table_suffix} "
        f"PARTITION OF course_completion_events "
        f"FOR VALUES FROM ('{start_date}') TO ('{end_date}');"
    )
    
    course_idx_sql = (
        f"CREATE INDEX IF NOT EXISTS course_completion_events_{table_suffix}_course_id_idx "
        f"ON course_completion_events_{table_suffix} (course_id);"
    )
    
    timestamp_idx_sql = (
        f"CREATE INDEX IF NOT EXISTS course_completion_events_{table_suffix}_event_timestamp_idx "
        f"ON course_completion_events_{table_suffix} (event_timestamp);"
    )
    
    return f"{create_table_sql}\n{course_idx_sql}\n{timestamp_idx_sql}"