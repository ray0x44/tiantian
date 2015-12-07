# coding=utf-8

from flask import (make_response, render_template, Response)
from wechat import Wechat
from log.logger import log
from wechat_sdk.exceptions import *
from wechat_sdk.messages import *


def check_signature(request):
    args = request.args
    signature = args.get('signature')
    timestamp = args.get('timestamp')
    nonce = args.get('nonce')
    echostr = args.get('echostr')
    if Wechat().check_signature(signature, timestamp, nonce):
        return echostr or ''
    return Response(status=204)

def handle_client(request):
    wechat = Wechat()
    args = request.args
    # check request signature
    if not wechat.check_signature(args.get('signature'), args.get('timestamp'), args.get('nonce')):
        return ''
    try:
        wechat.parse_data(request.data)
    except ParseError:
        log.error('Parse post data error, data: %s'%str(request.data))
        return ''

    message = wechat.get_message()
    response = None
    # normal message
    if isinstance(message, TextMessage):
        response = wechat.response_text(content=u'文字信息')
    elif isinstance(message, VoiceMessage):
        response = wechat.response_text(content=u'语音信息')
    elif isinstance(message, ImageMessage):
        response = wechat.response_text(content=u'图片信息')
    elif isinstance(message, VideoMessage):
        response = wechat.response_text(content=u'视频信息')
    elif isinstance(message, ShortVideoMessage):
        response = wechat.response_text(content=u'小视频信息')
    elif isinstance(message, LinkMessage):
        response = wechat.response_text(content=u'链接信息')
    elif isinstance(message, LocationMessage):
        response = wechat.response_text(content=u'地理位置信息')
    # event message
    elif isinstance(message, EventMessage):  # 事件信息
        if message.type == 'subscribe':  # 关注事件(包括普通关注事件和扫描二维码造成的关注事件)
            if message.key and message.ticket:  # 如果 key 和 ticket 均不为空，则是扫描二维码造成的关注事件
                response = wechat.response_text(content=u'用户尚未关注时的二维码扫描关注事件')
            else:
                response = wechat.response_text(content=u'普通关注事件')
        elif message.type == 'unsubscribe':
            response = wechat.response_text(content=u'取消关注事件')
        elif message.type == 'scan':
            response = wechat.response_text(content=u'用户已关注时的二维码扫描事件')
        elif message.type == 'location':
            response = wechat.response_text(content=u'上报地理位置事件')
        elif message.type == 'click':
            response = wechat.response_text(content=u'自定义菜单点击事件')
        elif message.type == 'view':
            response = wechat.response_text(content=u'自定义菜单跳转链接事件')
        elif message.type == 'templatesendjobfinish':
            response = wechat.response_text(content=u'模板消息事件')

    return make_response(response)
