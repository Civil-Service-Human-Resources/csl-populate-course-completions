import json
import psycopg
import uuid
import os
import partitionSql

conn_info = f"dbname={os.getenv('DB_NAME')} user={os.getenv('DB_USERNAME')} password={os.getenv('DB_PASSWORD')} host={os.getenv('DB_HOST')} port={os.getenv('DB_PORT')}"

sql_insert_template = "INSERT INTO course_completion_events (external_id, event_timestamp, user_id, user_email, course_id, course_title, organisation_id, organisation_name, profession_id, profession_name, grade_id, grade_name) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

with open("/output/extracted_course_data.json", "r") as f:
    extracted_messages = json.load(f)

successful_inserts = []
failed_inserts = []

with psycopg.connect(conn_info) as conn:
    with conn.cursor() as cur:
        for message in extracted_messages:
            external_id = uuid.uuid4()
            metadata = message.get("metadata", {})
            event_timestamp = metadata.get("completionDate")
            user_id = metadata.get("userId")
            user_email = metadata.get("userEmail")
            course_id = metadata.get("courseId")
            course_title = metadata.get("courseTitle")
            organisation_id = metadata.get("organisationId")
            organisation_name = metadata.get("organisationName")
            profession_id = metadata.get("professionId")
            profession_name = metadata.get("professionName")
            grade_id = None if metadata.get("gradeId") == "null" else metadata.get("gradeId")
            grade_name = None if metadata.get("gradeName") == "null" else metadata.get("gradeName")

            try:
                partition_sql = partitionSql.generate_partition_and_indices_sql(event_timestamp)
                cur.execute(partition_sql)
                cur.execute(
                    sql_insert_template,
                    (
                        external_id,
                        event_timestamp,
                        user_id,
                        user_email,
                        course_id,
                        course_title,
                        organisation_id,
                        organisation_name,
                        profession_id,
                        profession_name,
                        grade_id,
                        grade_name,
                    ),
                )        
                conn.commit()
                successful_inserts.append(message)
            except Exception as e:
                print("Error inserting message:", e)
                failed_inserts.append(message)
                conn.rollback() 
                continue

print("Failed inserts: ", len(failed_inserts))

with open("/output/successful_inserts.json", "w") as f:
    json.dump(successful_inserts, f, indent=4)

with open("/output/failed_inserts.json", "w") as f:
    json.dump(failed_inserts, f, indent=4)