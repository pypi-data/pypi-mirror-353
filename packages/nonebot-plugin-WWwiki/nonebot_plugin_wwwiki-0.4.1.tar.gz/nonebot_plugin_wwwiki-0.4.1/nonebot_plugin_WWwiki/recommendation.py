# coding=utf-8
import httpx
import json

from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot import on_command

from .getskll import get_recommendation
from .basicinformation import get_basic_information
from .judgmentrolename import judgment_role_name
from .itemlink import get_link
from .pil_draw.draw import draw_main
from .util import UniMessage, get_template,template_to_pic

html_spath = get_template("recommendation")


recommendation_cards = on_command('鸣潮角色养成推荐')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0',
    'Referer': 'https://wiki.kurobbs.com/',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Sec-Ch-Ua': '"Microsoft Edge";v="125", "Chromium";v="125", "Not=A?Brand";v="24"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Wiki_type': '9'

}
listdata = {
    'catalogueId': '1105',
    'page': '1',
    'limit': '1000'
}


@recommendation_cards.handle()
async def recommendationcards(args: Message = CommandArg()):
    role_name = judgment_role_name(args.extract_plain_text())
    role_id = await get_link(role_name, listdata)
    if role_id is None:
        await recommendation_cards.finish(f'没有找到角色,错误参数：' + role_name)
    else:
        roledata = {
            'id': role_id
        }

        async with httpx.AsyncClient() as client:
            roledataurl = 'https://api.kurobbs.com/wiki/core/catalogue/item/getEntryDetail'
            roledata_r = await client.post(roledataurl, data=roledata, headers=headers)
            data = json.loads(roledata_r.text)

            info_data = get_basic_information(data)
            components=data['data']['content']['modules'][2]['components']
            component = next((r for r in components if r.get('title') in ('角色搭配推荐','角色养成推荐')), None)
            # for item in components:
            if component:
                item = component
                weapons_recommended_data = item['tabs'][0]['content']
                weapons_recommended = get_recommendation(weapons_recommended_data)
                echo_recommended_data = item['tabs'][1]['content']
                echo_recommended = get_recommendation(echo_recommended_data)
                team_recommended_data = item['tabs'][2]['content']
                team_recommended = get_recommendation(team_recommended_data)
                skll_recommended_data = item['tabs'][3]['content']
                skll_recommended = get_recommendation(skll_recommended_data)

                Data = {
                    'roleimg': info_data.get('role_img'),
                    'rolename': info_data.get('role_name'),
                    'campIcon': info_data.get('campIcon'),
                    'roleenname': info_data.get('role_en_name'),
                    'roledescription': info_data.get('role_description'),
                    'roledescriptiontitle': info_data.get('role_description_title'),
                    'weapons_recommended': weapons_recommended,
                    'echo_recommended': echo_recommended,
                    'team_recommended': team_recommended,
                    'skll_recommended': skll_recommended
                }

                img = await template_to_pic(
                    html_spath.parent.as_posix(),
                    html_spath.name,
                    Data,
                )

                await UniMessage.image(raw=img).finish()
            else:
                await recommendation_cards.finish('角色暂无养成推荐,请尝试使用一图流')
