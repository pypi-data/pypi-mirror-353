from ximalaya.core.client import XimalayaClient, ResponsePaginator
from ximalaya.core.models import AlbumInfo


def api_category_v2_albums(client: XimalayaClient, *, category_id: int, page_size: int = 50, sort_by: int = 1) -> ResponsePaginator[AlbumInfo]:
    client.host = 'www.ximalaya.com'

    return ResponsePaginator(
        client,
        url='/revision/category/v2/albums',
        params={'pageSize': page_size, 'sort': sort_by, 'categoryId': category_id},
        item_class=AlbumInfo,
        page_key='pageNum',
        data_path='data.albums'
    )
