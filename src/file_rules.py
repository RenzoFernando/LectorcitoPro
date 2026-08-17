import os

def normalize_file_rule(value: str) -> str:
    return (value or "").strip().lower()


def canonical_file_rule(value: str) -> str:
    return normalize_file_rule(value).lstrip(".")


def file_rules_conflict(rule_a: str, rule_b: str) -> bool:
    normalized_a = normalize_file_rule(rule_a)
    normalized_b = normalize_file_rule(rule_b)

    if not normalized_a or not normalized_b:
        return False

    return normalized_a == normalized_b or canonical_file_rule(normalized_a) == canonical_file_rule(normalized_b)


def normalize_file_tag_list(tag_list: list | None) -> list[dict]:
    normalized_tags = []
    for tag in tag_list or []:
        if not isinstance(tag, dict):
            continue
        normalized_name = normalize_file_rule(tag.get("nombre", ""))
        if not normalized_name:
            continue
        normalized_tags.append({
            "nombre": normalized_name,
            "estado": tag.get("estado", "activo")
        })
    return normalized_tags


def normalize_file_rule_list(rule_list: list | None) -> list[str]:
    normalized_rules = []
    for rule in rule_list or []:
        normalized_rule = normalize_file_rule(rule)
        if normalized_rule:
            normalized_rules.append(normalized_rule)
    return normalized_rules


def matches_file_rule(filename: str, rules: set | list) -> bool:
    filename_normalized = normalize_file_rule(filename)
    _, ext = os.path.splitext(filename_normalized)
    ext_without_dot = ext[1:] if ext.startswith(".") else ext

    for rule in rules:
        rule_normalized = normalize_file_rule(rule)
        if not rule_normalized:
            continue
        if filename_normalized == rule_normalized:
            return True
        if ext_without_dot and canonical_file_rule(rule_normalized) == ext_without_dot:
            return True
    return False
