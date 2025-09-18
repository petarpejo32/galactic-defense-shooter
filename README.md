# Galactic Defense Shooter

**Автор:** Петар Пејоски - 211551  
**Предмет:** Програмирање на видео игри

## Опис

2D space shooter игра со модуларна архитектура, звучни ефекти, boss битки и специјална mothership битка на 200 поени.

## Инсталација и стартување

```bash
pip install -r requirements.txt
python main.py
```

## Контроли

- **Стрелки**: Движење
- **SPACE**: Пукање  
- **P**: Пауза
- **1/2/3**: Тежина на игра
- **ENTER**: Почни игра

## Функционалности

### Основни функции
- **Играч**: Движење, пукање, здравје ,муниција
- **Непријатели**: 3 типа (basic, heavy, fast) со различни движења
- **Boss битки**: Multi-phase boss со прогресивни напади
- **Power-ups**: 5 типа (triple shot, shield, health, speed, ammo)

### Напредни функции  
- **Mothership битка**: Се активира на 200 поени, 3 фази на напад
- **Звучни ефекти**: 13 звуци + позадинска музика
- **Системи за муниција**: Ограничена муниција со reload
- **Тежина**: Easy/Normal/Hard со различни параметри
- **Particle ефекти**: Експлозии и визуелни ефекти

## Техничка имплементација

### Архитектура
```
main.py          - Влезна
game.py          - Главна
entities.py      - Играч, непријатели, куршуми
graphics.py      - Цртање на бродови и ефекти
effects.py       - Particle систем и нотификации
sound_manager.py - Аудио систем
constants.py     - Константи и бои
```

### Програмски концепти
- **OOP дизајн**: Класи за сите entity-ја
- **State управување**: Menu → Difficulty → Playing → Game Over
- **Collision detection**: Rectangle-базирано
- **Sound систем**: Looping музика и еднократни ефекти
- **Progressive difficulty**: Динамичко прилагодување

## Скриншоти

### Главно мени
- Мени со опции за тежина
- High score приказ

### Игра во тек
- Играч со ограничено здравје и индикатор за муниција
- Непријатели од различни типови
- Power-ups со glow ефекти
- Info panel со упатства

### Boss битка  
- Boss со health bar и multi-phase напади
- Particle ефекти при погодоци

### Mothership битка
- Зелена позадина за атмосфера
- "MOTHERSHIP BATTLE" текст
- 3-фазни напади (single → triple → spray)

## Видео демо

- **Во Главниот фолдер**

## Технички детали

- **Резолуција**: 1200×900 (900×900 игра + 300px info)
- **FPS**: 60
- **Pygame**: 2.0+
- **Звучни формати**: WAV/MP3
- **Големина**: ~10MB вкупно

## Развој

Играта демонстрира:
1. **Модуларен код**
2. **Комплетен game loop**
3. **Аудио интеграција** - sound manager со error handling

## Датотеки за предавање

- Изворен код (7 Python датотеки)
- requirements.txt
- sounds/ фолдер (13 аудио датотеки)
- README.md

**GitHub**: https://github.com/petarpejo32/galactic-defense-shooter

## Референци

- Pygame документација: https://www.pygame.org/docs/
- Sound design концепти од OpenGameArt.org
