from datetime import datetime

from ximalaya.core.client import XimalayaClient, ResponsePaginator
from ximalaya.core.models import AlbumComment


def api_album_comment_list(client: XimalayaClient, *, album_id: int, page_size: int = 50, order: str = 'content-score-desc') -> ResponsePaginator[AlbumComment]:
    client.host = 'mobile.ximalaya.com'
    timestamp = int(datetime.now().timestamp() * 1000)

    return ResponsePaginator(
        client,
        url=f'/album-comment-mobile/web/album/comment/list/query/{timestamp}',
        params={'albumId': album_id, 'order': order, 'pageSize': page_size},
        item_class=AlbumComment,
        data_path='data.comments.list',
        page_key='pageId'
    )
