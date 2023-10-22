import requests
import re
import xml.etree.ElementTree as ET
from xml.dom import minidom
import os
import html

def main():
    output_file = "makeRSS_GIGAZINE.xml"
    feed = {
        "url": "https://gigazine.net/news/rss_2.0/",
        "includeWords": ["AI", "ChatGPT", "DX", "自動化", "RPA", "ノーコード", "ローコード"]
    }
    
    # 既存のRSSフィードを読み込む
    existing_links = set()
    if os.path.exists(output_file):
        tree = ET.parse(output_file)
        root = tree.getroot()
        for item in root.findall(".//item/link"):
            existing_links.add(item.text)
    else:
        root = ET.Element("rss", version="2.0")
        channel = ET.SubElement(root, "channel")
        title = "GIGAZINEの特定のキーワードを含むRSS"
        description = "GIGAZINEから特定のキーワードを含む記事を提供します。"
        ET.SubElement(channel, "title").text = title
        ET.SubElement(channel, "description").text = description
        ET.SubElement(channel, "link").text = "https://example.com"
        
    url = feed["url"]
    includeWords = feed["includeWords"]
    response = requests.get(url)
    rss_content = response.text
    
    items = re.findall(r"<item[^>]*>([\s\S]*?)<\/item>", rss_content)
    channel = root.find("channel")
    
    for item in items:
        title = re.search(r"<title>(.*?)<\/title>", item).group(1)
        link = re.search(r"<link>(.*?)<\/link>", item).group(1)

        # HTMLエンティティをデコード
        link = html.unescape(link)
        
        # 既存のリンクならスキップ
        if link in existing_links:
            continue
        
        description = re.search(r"<description>([\s\S]*?)<\/description>", item).group(1)
        date = re.search(r"<pubDate>(.*?)<\/pubDate>", item).group(1)
        
        if any(word in title or word in description for word in includeWords):
            new_item = ET.SubElement(channel, "item")
            ET.SubElement(new_item, "title").text = title
            ET.SubElement(new_item, "link").text = link
            ET.SubElement(new_item, "description").text = description
            ET.SubElement(new_item, "pubDate").text = date

    xml_str = ET.tostring(root)
    xml_str = re.sub(u'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', xml_str.decode()).encode()
    xml_pretty_str = minidom.parseString(xml_str).toprettyxml(indent="  ")
    
    # 余分な空白行を削除
    xml_pretty_str = os.linesep.join([line for line in xml_pretty_str.splitlines() if line.strip()])

    with open(output_file, "w") as f:
        f.write(xml_pretty_str)

if __name__ == "__main__":
    main()
