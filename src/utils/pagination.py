def paginate(items: list, page: int = 1, per_page: int = 5):
    """
    صفحه‌بندی یک لیست ساده
    
    Returns:
        {
            "items": [...],
            "page": page,
            "total_pages": total_pages
        }
    """
    total_items = len(items)
    total_pages = max(1, (total_items + per_page - 1) // per_page)

    # جلوگیری از صفحه غیرمجاز
    page = max(1, min(page, total_pages))

    start = (page - 1) * per_page
    end = start + per_page
    paginated_items = items[start:end]

    return {
        "items": paginated_items,
        "page": page,
        "total_pages": total_pages
    }
