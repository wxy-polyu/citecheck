"""Print whether the language-model settings are present. Does not call the API."""

from citecheck.llm import load_settings


def main() -> None:
    settings = load_settings()
    key_state = "已设置" if settings["api_key"] else "未设置"
    print(f"LLM_BASE_URL: {settings['base_url']}")
    print(f"LLM_MODEL: {settings['model']}")
    print(f"LLM_API_KEY: {key_state}")


if __name__ == "__main__":
    main()
