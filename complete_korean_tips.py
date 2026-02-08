#!/usr/bin/env python3
"""
Script per completare la traduzione coreana del file tips.html aggiungendo le 8 sezioni mancanti.
"""

# Dizionario di traduzioni inglese -> coreano
translations_ko = {
    "Gear": "장비",
    "Level": "레벨",
    "Enhance Rune": "강화 룬",
    "Ruby": "루비",
    "Gold ingot": "금괴",
    "Promotion Stone": "승급석",
    "Gear Stars": "장비 별",
    "Total": "합계",
    "Total till this level": "이 레벨까지 총합",
    "Exclusive Gear": "전용 장비",
    "Lord Gear": "영주 장비",
    "Star level": "별 레벨",
    "Refined metal": "정제된 금속",
    "Magic Thread": "마법 실",
    "Orichalcum": "오리하르콘",
    "Common": "일반",
    "Rare": "희귀",
    "Epic": "에픽",
    "Legendary": "전설",
    "Mythic": "신화",
    "Troop Skin": "부대 스킨",
    "Step": "단계",
    "Medals": "메달",
    "Universal Shard": "범용 파편",
    "Rare skin": "희귀 스킨",
    "Epic skin": "에픽 스킨",
    "Legend skin": "전설 스킨",
    "Rare Troop Skin": "희귀 부대 스킨",
    "Epic Troop Skin": "에픽 부대 스킨",
    "Legendary Troop Skin": "전설 부대 스킨",
    "Relic": "유물",
    "Star Level": "별 레벨",
    "Shard for single up": "단일 업그레이드 파편",
    "Shards Full Star": "풀스타 파편",
    "Rare Relic": "희귀 유물",
    "Epic Relic": "에픽 유물",
    "Legendary Relic": "전설 유물",
    "Rare relic": "희귀 유물",
    "Epic relic": "에픽 유물",
    "Leg relic": "전설 유물",
    "Rune": "룬",
    "Hero HP": "영웅 HP",
    "Hero Attack": "영웅 공격력",
    "Soldier HP": "병사 HP",
    "Soldier Attack": "병사 공격력",
    "March Size": "행군 규모",
    "Relic Mastery": "유물 숙련도",
    "Queue Attack": "대기열 공격",
    "Defense": "방어",
    "Defense Break": "방어 관통",
    "HP of All Soldiers": "모든 병사 HP",
    "Attack of All Soldiers": "모든 병사 공격력",
    "Hero HP Rune": "영웅 HP 룬",
    "Hero Attack Rune": "영웅 공격력 룬",
    "Soldier HP Rune": "병사 HP 룬",
    "Soldier Attack Rune": "병사 공격력 룬",
    "Relic Mastery Rune": "유물 숙련도 룬",
    "Queue Attack Rune": "대기열 공격 룬",
    "Relic HP": "유물 HP",
    "Pet": "애완동물",
    "Pet Food": "펫 음식",
    "Promotion": "승급",
    "Pet needed": "필요한 펫",
    "Pet essence": "펫 에센스",
    "Villager": "마을 주민",
    "Villagers": "마을 주민",
    "Building": "건물",
    "Attribute": "속성",
    "Castle": "성",
    "Research Cottage": "연구소",
    "Guild": "길드",
    "League Barracks": "리그 막사",
    "Horde Barracks": "호드 막사",
    "Nature Barracks": "자연 막사",
    "Hospital": "병원",
    "Queue": "대기열",
    "Training Ground": "훈련장",
    "Watchtower": "감시탑",
    "Tavern": "선술집",
    "VIP": "VIP",
    "$ Estimated": "$ 예상",
    "Points": "포인트",
    "Back to top": "맨 위로 돌아가기",
    "League Statue": "리그 석상",
    "Horde Statue": "호드 석상",
    "Nature Statue": "자연 석상",
    "Troop Skin Center": "부대 스킨 센터",
    "Medal Hall": "메달 홀",
    "Hero Statue": "영웅 석상",
    "Magic Stone Mine": "마법석 광산",
    "Medal Monument": "메달 기념비",
    "Pet Food Factory": "펫 음식 공장",
    "Enhance Rune Mine": "강화 룬 광산",
    "Monastery": "수도원",
    "Raw Ore Mine": "원광석 광산",
    "Ranch": "목장",
    "Stone Mine": "석재 광산",
    "Ruby Mine": "루비 광산",
    "Sawmill": "제재소",
    "Warehouse": "창고",
    "Blacksmith": "대장간"
}

def translate_text(text):
    """Translate English text to Korean"""
    for eng, kor in translations_ko.items():
        text = text.replace(eng, kor)
    return text

def read_english_sections():
    """Read the 8 missing sections from English file"""
    with open('/workspaces/LucaViberti.github.io/html/tips.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find sections from <section id="gear"> to end of <section id="vip">
    import re
    
    # Extract Gear section
    gear_match = re.search(r'<section id="gear".*?</section>', content, re.DOTALL)
    gear_section = gear_match.group(0) if gear_match else ""
    
    # Extract Lord Gear section  
    lord_gear_match = re.search(r'<section id="lord-gear".*?</section>', content, re.DOTALL)
    lord_gear_section = lord_gear_match.group(0) if lord_gear_match else ""
    
    # Extract Troop Skin section
    skin_match = re.search(r'<section id="skin".*?</section>', content, re.DOTALL)
    skin_section = skin_match.group(0) if skin_match else ""
    
    # Extract Relic section
    relic_match = re.search(r'<section id="relic".*?</section>', content, re.DOTALL)
    relic_section = relic_match.group(0) if relic_match else ""
    
    # Extract Rune section
    rune_match = re.search(r'<section id="rune".*?</section>', content, re.DOTALL)
    rune_section = rune_match.group(0) if rune_match else ""
    
    # Extract Pet section
    pet_match = re.search(r'<section id="pet".*?</section>', content, re.DOTALL)
    pet_section = pet_match.group(0) if pet_match else ""
    
    # Extract Villager section
    villager_match = re.search(r'<section id="villager".*?</section>', content, re.DOTALL)
    villager_section = villager_match.group(0) if villager_match else ""
    
    # Extract VIP section
    vip_match = re.search(r'<section id="vip".*?</section>', content, re.DOTALL)
    vip_section = vip_match.group(0) if vip_match else ""
    
    return [gear_section, lord_gear_section, skin_section, relic_section, 
            rune_section, pet_section, villager_section, vip_section]

def append_sections_to_korean():
    """Append the 8 translated sections to Korean tips.html"""
    # Read Korean file
    with open('/workspaces/LucaViberti.github.io/ko/html/tips.html', 'r', encoding='utf-8') as f:
        korean_content = f.read()
    
    # Find the end of Hero section (before closing section tag)
    # We need to insert before the </div></main> closing tags
    
    # Get English sections
    sections = read_english_sections()
    
    # Translate sections
    translated_sections = []
    for section in sections:
        translated = translate_text(section)
        translated_sections.append(translated)
    
    # Find insertion point (after last </section> of Hero, before </div></main>)
    import re
    match = re.search(r'(</section>\s*)(</div>\s*</main>)', korean_content, re.DOTALL)
    
    if match:
        # Insert all translated sections between Hero section and closing div
        new_content = (korean_content[:match.start(2)] + 
                      '\n\n      ' + '\n\n      '.join(translated_sections) + 
                      '\n    ' + korean_content[match.start(2):])
        
        # Write back
        with open('/workspaces/LucaViberti.github.io/ko/html/tips.html', 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ Successfully added 8 sections to Korean tips.html!")
        print(f"   Total sections translated: {len(translated_sections)}")
    else:
        print("❌ Could not find insertion point in Korean file")

if __name__ == "__main__":
    append_sections_to_korean()
