from __future__ import annotations

from pydantic import BaseModel
from typing import Optional


class AlbumComment(BaseModel):
    albumId: int
    albumPaid: bool
    albumUid: int
    anchorLiked: bool
    auditStatus: int
    commentId: int
    content: str
    createdAt: int
    isHighQuality: bool
    likeStatus: Optional[int] = 0
    liked: Optional[bool] = False
    likes: int
    nickname: str
    playProgress: int
    recStatus: Optional[int] = 0
    region: str
    replyCount: int
    smallHeader: str
    uid: int
    updatedAt: int
    userTags: list[UserTag]
    vLogoType: int
    vipIconUrl: Optional[str] = None
    vipJumpUrl: Optional[str] = None


class AlbumInfo(BaseModel):
    albumId: int
    albumPlayCount: int
    albumTrackCount: int
    albumCoverPath: str
    albumTitle: str
    albumUserNickName: str
    anchorId: int
    anchorGrade: int
    mvpGrade: int
    isDeleted: bool
    isPaid: bool
    isFinished: int
    anchorUrl: str
    albumUrl: str
    intro: str
    vipType: int
    logoType: int
    subscriptInfo: SubscriptInfo
    albumSubscript: int


class AnchorInfo(BaseModel):
    anchorUrl: str
    anchorNickName: str
    anchorUid: int
    anchorCoverPath: str
    logoType: int


class FollowingInfo(BaseModel):
    uid: int
    coverPath: str
    anchorNickName: str
    background: str
    description: Optional[str] = None
    url: str
    grade: int
    mvpGrade: int
    gradeType: int
    trackCount: int
    albumCount: int
    followerCount: int
    followingCount: int
    isFollow: bool
    beFollow: bool
    isBlack: bool
    logoType: int


class FollowingPageInfo(BaseModel):
    totalCount: int
    followInfoList: list[FollowingInfo]


class LiveInfo(BaseModel):
    id: int = -1
    roomId: Optional[int] = None
    coverPath: Optional[str] = None
    liveUrl: Optional[str] = None
    status: Optional[int] = None


class PubInfo(BaseModel):
    id: int
    title: str
    subTitle: str
    coverPath: str
    isFinished: bool
    isPaid: bool
    anchorUrl: str
    anchorNickname: Optional[str] = None
    anchorUid: int
    playCount: int
    trackCount: int
    albumUrl: str
    description: str
    vipType: int
    albumSubscript: int


class PubPageInfo(BaseModel):
    totalCount: int
    pubInfoList: list[PubInfo]


class QualificationGuideInfo(BaseModel):
    guideMsg: str
    guideLinkUrl: str


class SubscriptInfo(BaseModel):
    albumSubscriptValue: int
    url: str


class SubscriptionInfo(BaseModel):
    id: int
    title: str
    subTitle: str
    description: str
    coverPath: str
    isFinished: bool
    isPaid: bool
    anchor: AnchorInfo
    playCount: int
    trackCount: int
    albumUrl: str
    albumStatus: int
    lastUptrackAt: int
    lastUptrackAtStr: str
    serialState: int
    isTop: bool
    categoryCode: str
    categoryTitle: str
    lastUptrackUrl: str
    lastUptrackTitle: str
    vipType: int
    albumSubscript: int
    albumScore: str


class SubscriptionPageInfo(BaseModel):
    privateSub: bool
    totalCount: int
    subscribeInfoList: list[SubscriptionInfo]


class TrackInfo(BaseModel):
    trackId: int
    title: str
    trackUrl: str
    coverPath: str
    createTimeAsString: str
    albumId: int
    albumTitle: str
    albumUrl: str
    anchorUid: int
    anchorUrl: str
    nickname: str
    durationAsString: str
    playCount: int
    showLikeBtn: bool
    isLike: bool
    isPaid: bool
    isRelay: bool
    showDownloadBtn: bool
    showCommentBtn: bool
    showForwardBtn: bool
    isVideo: bool
    videoCover: str
    breakSecond: int
    length: int
    isAlbumShow: bool


class TrackPageInfo(BaseModel):
    totalCount: int
    trackInfoList: list[TrackInfo]


class UserBasicInfo(BaseModel):
    uid: int
    nickName: str
    cover: str
    background: str
    isVip: bool
    constellationType: int
    personalSignature: Optional[str] = None
    personalDescription: Optional[str] = None
    fansCount: int
    gender: int
    birthMonth: int
    birthDay: int
    province: Optional[str] = None
    city: Optional[str] = None
    anchorGrade: int
    mvpGrade: int
    anchorGradeType: int
    isMusician: bool
    anchorUrl: str
    relation: UserRelation | None
    liveInfo: LiveInfo
    logoType: int
    followingCount: int
    tracksCount: int
    albumsCount: int
    albumCountReal: int
    userCompany: str
    qualificationGuideInfos: list[QualificationGuideInfo]


class UserDetailedInfo(BaseModel):
    uid: int
    pubPageInfo: PubPageInfo
    trackPageInfo: TrackPageInfo
    subscriptionPageInfo: SubscriptionPageInfo
    followingPageInfo: FollowingPageInfo


class UserRelation(BaseModel):
    isFollow: bool
    beFollow: bool
    isBlack: bool


class UserTag(BaseModel):
    businessName: str
    businessType: int
    extra: dict
    height: int
    icon: str
    jumpUrl: str
    scale: int
    width: int
