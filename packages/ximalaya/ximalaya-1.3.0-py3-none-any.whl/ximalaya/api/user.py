from ximalaya.core.client import XimalayaClient, ResponsePaginator
from ximalaya.core.models import FollowingInfo, UserBasicInfo, UserDetailedInfo, SubscriptionInfo


def api_user_following(client: XimalayaClient, *, uid: int, page_size: int = 50) -> ResponsePaginator[FollowingInfo]:
    client.host = 'www.ximalaya.com'

    return ResponsePaginator(
        client,
        url=f'/revision/user/following',
        params={'uid': uid, 'pageSize': page_size},
        item_class=FollowingInfo,
        data_path='data.followingsPageInfo'
    )


def api_user_basic(client: XimalayaClient, *, uid: int) -> UserBasicInfo:
    client.host = 'www.ximalaya.com'

    return UserBasicInfo(**client.get(f'/revision/user/basic?uid={uid}')['data'])


def api_user(client: XimalayaClient, *, uid: int) -> UserDetailedInfo:
    client.host = 'www.ximalaya.com'

    return UserDetailedInfo(**client.get(f'/revision/user?uid={uid}')['data'])


def api_user_sub(client: XimalayaClient, *, uid: int, page_size: int = 10) -> ResponsePaginator[SubscriptionInfo]:
    client.host = 'www.ximalaya.com'

    return ResponsePaginator(
        client,
        url='/revision/user/sub',
        params={'uid': uid, 'pageSize': page_size},
        item_class=SubscriptionInfo,
        data_path='data.albumsInfo'
    )
