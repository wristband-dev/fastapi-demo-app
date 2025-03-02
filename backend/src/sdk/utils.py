

def to_bool(env_val: str) -> bool:
        return env_val.strip().lower() in ["true", "1", "yes"]