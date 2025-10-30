import html
import re
from markdown import markdown
from bleach import clean

def sanitize_html(text):
    """
    Санитизация HTML для предотвращения XSS
    """
    if not text:
        return text
    
    # Базовое экранирование HTML
    sanitized = html.escape(text)
    
    return sanitized

def sanitize_user_input(input_data):
    """
    Санитизация пользовательского ввода
    """
    if isinstance(input_data, str):
        # Удаляем потенциально опасные символы
        sanitized = re.sub(r'[<>"\'&]', '', input_data)
        # Ограничиваем длину
        return sanitized[:1000]
    elif isinstance(input_data, dict):
        return {key: sanitize_user_input(value) for key, value in input_data.items()}
    elif isinstance(input_data, list):
        return [sanitize_user_input(item) for item in input_data]
    else:
        return input_data

def safe_markdown_to_html(markdown_text):
    """
    Безопасное преобразование Markdown в HTML
    """
    if not markdown_text:
        return ""
    
    # Разрешаем только безопасные теги
    allowed_tags = [
        'p', 'br', 'strong', 'em', 'ul', 'ol', 'li', 
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote'
    ]
    
    allowed_attributes = {
        '*': ['class'],
        'a': ['href', 'title'],
        'img': ['src', 'alt', 'title']
    }
    
    html_content = markdown(markdown_text)
    safe_html = clean(
        html_content,
        tags=allowed_tags,
        attributes=allowed_attributes,
        strip=True
    )
    
    return safe_html