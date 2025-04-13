from django.core.exceptions import ValidationError

def validate_file_size(file):
    max_size = 50
    max_size_in_kb = max_size * 1024

    if file.size > max_size_in_kb:
        raise ValidationError(f"Your file size is {file.size} KB. But, it can't be more than 50 KB")
    