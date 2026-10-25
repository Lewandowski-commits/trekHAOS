import json
import sqlite3
import time
import os
import uuid

HA_AUTH_PROVIDER = "/config/.storage/auth_provider.homeassistant"
HA_AUTH = "/config/.storage/auth"
TREK_DB = "/app/data/trek.db"

def get_ha_users():
    if not os.path.exists(HA_AUTH_PROVIDER) or not os.path.exists(HA_AUTH):
        return {}
    
    with open(HA_AUTH_PROVIDER) as f:
        provider_data = json.load(f)
    with open(HA_AUTH) as f:
        auth_data = json.load(f)
        
    auth_users = {u["id"]: u for u in auth_data.get("data", {}).get("users", [])}
    
    ha_users = {}
    for pu in provider_data.get("data", {}).get("users", []):
        uid = pu.get("id")
        if uid in auth_users:
            if auth_users[uid].get("system_generated"):
                continue
            
            username = pu.get("username")
            password = pu.get("password")
            name = auth_users[uid].get("name") or username
            email = username if "@" in username else f"{username}@homeassistant.local"
            ha_users[email] = {
                "password": password,
                "name": name,
                "username": username
            }
            
    return ha_users

def sync():
    while True:
        try:
            ha_users = get_ha_users()
            if ha_users:
                conn = sqlite3.connect(TREK_DB)
                cursor = conn.cursor()
                
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Users'")
                if not cursor.fetchone():
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
                    if not cursor.fetchone():
                        conn.close()
                        time.sleep(60)
                        continue
                    else:
                        table_name = "users"
                else:
                    table_name = "Users"

                cursor.execute(f"SELECT email, role, id FROM {table_name}")
                existing_users = {row[0]: {"role": row[1], "id": row[2]} for row in cursor.fetchall()}
                
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = [c[1] for c in cursor.fetchall()]
                has_username = "username" in columns
                has_provider = "provider" in columns
                
                for email, data in ha_users.items():
                    name = data["name"]
                    password = data["password"]
                    username = data["username"]
                    
                    if email in existing_users:
                        if existing_users[email]["role"] == "admin":
                            continue
                        
                        query = f"UPDATE {table_name} SET password = ?, name = ? WHERE email = ?"
                        cursor.execute(query, (password, name, email))
                    else:
                        user_id = str(uuid.uuid4())
                        
                        insert_cols = ["id", "email", "name", "password", "role"]
                        insert_vals = [user_id, email, name, password, "user"]
                        
                        if has_username:
                            insert_cols.append("username")
                            insert_vals.append(username)
                            
                        if has_provider:
                            insert_cols.append("provider")
                            insert_vals.append("homeassistant")
                            
                        placeholders = ",".join(["?"] * len(insert_vals))
                        query = f"INSERT INTO {table_name} ({','.join(insert_cols)}) VALUES ({placeholders})"
                        cursor.execute(query, insert_vals)
                
                conn.commit()
                conn.close()
        except Exception as e:
            print(f"Error syncing users: {e}")
            
        time.sleep(60)

if __name__ == "__main__":
    while not os.path.exists(TREK_DB):
        time.sleep(10)
    sync()
