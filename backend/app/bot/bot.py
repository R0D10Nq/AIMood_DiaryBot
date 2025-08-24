"""
Telegram Bot для AI Mood Diary Bot
Основной файл с обработчиками команд и сообщений
"""

import logging
import asyncio
from typing import Dict, Any
from datetime import datetime, date

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from telegram.constants import ParseMode

from ..core.config import settings
from ..core.database import SessionLocal
from ..crud.user import user_crud
from ..crud.mood_entry import mood_entry_crud
from ..services.mood_analyzer import mood_analyzer
from ..schemas import UserCreate, MoodEntryCreate

logger = logging.getLogger(__name__)


class MoodDiaryBot:
    """Telegram Bot для ведения дневника настроения"""
    
    def __init__(self):
        self.token = settings.TELEGRAM_BOT_TOKEN
        self.application = None
        self._user_states: Dict[int, Dict[str, Any]] = {}  # Состояния пользователей
    
    def setup_application(self):
        """Настройка приложения бота"""
        if not self.token:
            logger.error("❌ Telegram Bot Token не настроен!")
            return None
        
        # Создаем приложение
        self.application = Application.builder().token(self.token).build()
        
        # Добавляем обработчики команд
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("mood", self.mood_command))
        self.application.add_handler(CommandHandler("stats", self.stats_command))
        self.application.add_handler(CommandHandler("recommendations", self.recommendations_command))
        self.application.add_handler(CommandHandler("analytics", self.analytics_command))
        
        # Обработчик callback-кнопок
        self.application.add_handler(CallbackQueryHandler(self.handle_callback))
        
        # Обработчик текстовых сообщений
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        logger.info("✅ Telegram Bot настроен")
        return self.application
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        user = update.effective_user
        chat_id = update.effective_chat.id
        
        # Регистрируем пользователя в БД
        with SessionLocal() as db:
            user_data = {
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "language_code": user.language_code or "ru"
            }
            
            db_user, created = user_crud.get_or_create(db, user.id, user_data)
            
            if created:
                welcome_text = f"""
🎉 Добро пожаловать в AI Mood Diary Bot, {user.first_name or 'друг'}!

Я помогу вам вести дневник настроения и анализировать эмоциональное состояние с помощью искусственного интеллекта.

🔥 Что я умею:
• 📝 Записывать ваше настроение каждый день
• 🧠 Анализировать эмоции с помощью AI
• 📊 Показывать статистику и тренды
• 💡 Давать персональные рекомендации
• 🎯 Помочь лучше понимать себя

Начните с команды /mood чтобы записать настроение дня!
"""
            else:
                welcome_text = f"""
👋 С возвращением, {user.first_name or 'друг'}!

У вас уже {db_user.mood_entries_count} записей в дневнике. Продолжаем отслеживать ваше настроение!

Используйте /mood для новой записи или /stats для статистики.
"""
        
        # Создаем клавиатуру
        keyboard = [
            [KeyboardButton("📝 Записать настроение"), KeyboardButton("📊 Моя статистика")],
            [KeyboardButton("💡 Рекомендации"), KeyboardButton("📈 Аналитика")],
            [KeyboardButton("❓ Помощь")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /help"""
        help_text = """
🤖 *AI Mood Diary Bot - Справка*

📝 *Основные команды:*
/start - Начать работу с ботом
/mood - Записать настроение дня
/stats - Посмотреть статистику
/recommendations - Получить рекомендации
/analytics - Подробная аналитика
/help - Эта справка

🎯 *Как пользоваться:*

1️⃣ *Запись настроения:* Используйте /mood или кнопку "📝 Записать настроение"
2️⃣ *Оценка:* Поставьте оценку от 1 до 10
3️⃣ *Описание:* Опишите свое состояние и день
4️⃣ *AI анализ:* Получите автоматический анализ эмоций

📊 *Статистика и аналитика:*
• Средняя оценка настроения
• Тренды и изменения
• Доминирующие эмоции
• Персональные рекомендации

💡 *Советы:*
• Ведите дневник регулярно для лучшего анализа
• Будьте честны в описаниях
• Используйте рекомендации для улучшения настроения

❓ *Поддержка:* Если что-то не работает, напишите /help
"""
        await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)
    
    async def mood_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /mood - начало записи настроения"""
        user_id = update.effective_user.id
        
        # Проверяем, есть ли уже запись на сегодня
        with SessionLocal() as db:
            today_entry = mood_entry_crud.get_by_user_and_date(db, user_id, date.today())
            
            if today_entry:
                await update.message.reply_text(
                    f"📅 На сегодня у вас уже есть запись с оценкой {today_entry.mood_score}/10.\n\n"
                    f"Хотите посмотреть статистику (/stats) или записать настроение на завтра?"
                )
                return
        
        # Сохраняем состояние пользователя
        self._user_states[user_id] = {
            "action": "waiting_mood_score",
            "step": 1
        }
        
        # Создаем inline клавиатуру с оценками
        keyboard = []
        for row in range(2):
            keyboard_row = []
            for col in range(5):
                score = row * 5 + col + 1
                keyboard_row.append(InlineKeyboardButton(f"{score}", callback_data=f"mood_score_{score}"))
            keyboard.append(keyboard_row)
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "📊 *Оцените ваше настроение сегодня от 1 до 10:*\n\n"
            "1-2: Очень плохо 😞\n"
            "3-4: Плохо 😔\n"
            "5-6: Нормально 😐\n"
            "7-8: Хорошо 😊\n"
            "9-10: Отлично! 😄",
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /stats - статистика пользователя"""
        user_id = update.effective_user.id
        
        with SessionLocal() as db:
            # Получаем статистику
            summary = mood_analyzer.get_mood_summary(db, user_id, 7)
            
            if summary.get("total_entries", 0) == 0:
                await update.message.reply_text(
                    "📊 У вас пока нет записей в дневнике.\n\n"
                    "Начните с команды /mood для записи настроения дня!"
                )
                return
            
            # Формируем текст статистики
            stats_text = f"""
📊 *Ваша статистика за {summary['period_days']} дней:*

📈 Всего записей: {summary['total_entries']}
⭐ Среднее настроение: {summary['average_mood']}/10
📉 Тренд: {summary['mood_trend']}
🎭 Основная эмоция: {summary.get('dominant_emotion', 'неопределено')}

💾 Последняя запись: {summary.get('latest_entry_date', 'нет данных')}
"""
            
            # Добавляем распределение тональности
            if summary.get('sentiment_distribution'):
                sentiment = summary['sentiment_distribution']
                stats_text += f"\n🎯 *Распределение настроения:*\n"
                stats_text += f"• Позитивное: {sentiment.get('positive', 0)} дней\n"
                stats_text += f"• Нейтральное: {sentiment.get('neutral', 0)} дней\n"
                stats_text += f"• Негативное: {sentiment.get('negative', 0)} дней\n"
            
            # Добавляем кнопки для дополнительных действий
            keyboard = [
                [InlineKeyboardButton("📈 Подробная аналитика", callback_data="analytics")],
                [InlineKeyboardButton("💡 Рекомендации", callback_data="recommendations")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(stats_text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    
    async def recommendations_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /recommendations - рекомендации"""
        user_id = update.effective_user.id
        
        with SessionLocal() as db:
            recommendations = mood_analyzer.get_recommendations_for_user(db, user_id)
            
            if recommendations.get("error"):
                await update.message.reply_text(
                    "❌ Произошла ошибка при получении рекомендаций.\n"
                    "Попробуйте позже или напишите /help"
                )
                return
            
            # Формируем текст рекомендаций
            rec_text = f"💡 *Персональные рекомендации*\n\n"
            
            if recommendations.get("average_mood"):
                rec_text += f"📊 Среднее настроение: {recommendations['average_mood']}/10\n"
                rec_text += f"📅 Период анализа: {recommendations.get('period', 'последние записи')}\n\n"
            
            # AI рекомендации
            ai_recs = recommendations.get("ai_recommendations", [])
            if ai_recs:
                rec_text += "🧠 *Рекомендации от ИИ:*\n"
                for i, rec in enumerate(ai_recs, 1):
                    rec_text += f"{i}. {rec}\n"
                rec_text += "\n"
            
            # Общие рекомендации
            general_recs = recommendations.get("general_recommendations", [])
            if general_recs:
                rec_text += "🎯 *Общие рекомендации:*\n"
                for rec in general_recs:
                    rec_text += f"• {rec}\n"
            
            await update.message.reply_text(rec_text, parse_mode=ParseMode.MARKDOWN)
    
    async def analytics_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /analytics - подробная аналитика"""
        user_id = update.effective_user.id
        
        with SessionLocal() as db:
            # Получаем аналитику за месяц
            analytics = mood_entry_crud.get_mood_analytics(db, user_id, "month")
            
            if analytics.get("total_entries", 0) == 0:
                await update.message.reply_text(
                    "📈 Недостаточно данных для аналитики.\n\n"
                    "Ведите дневник регулярно для получения подробной статистики!"
                )
                return
            
            # Формируем текст аналитики
            analytics_text = f"""
📈 *Подробная аналитика за месяц:*

📊 *Общие показатели:*
• Всего записей: {analytics['total_entries']}
• Среднее настроение: {analytics['average_mood']}/10

🎭 *Распределение настроения:*
• Позитивное (7-10): {analytics['mood_distribution']['positive']} дней
• Нейтральное (4-6): {analytics['mood_distribution']['neutral']} дней  
• Негативное (1-3): {analytics['mood_distribution']['negative']} дней

📅 *Активность по дням:*
"""
            
            # Добавляем информацию о последних днях
            daily_data = analytics.get('daily_averages', [])
            if daily_data:
                for day in daily_data[-7:]:  # Последние 7 дней
                    analytics_text += f"• {day['date']}: {day['average_mood']}/10\n"
            
            # Кнопка для веб-интерфейса
            keyboard = [
                [InlineKeyboardButton("🌐 Открыть веб-дашборд", url="http://localhost:3000")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                analytics_text, 
                reply_markup=reply_markup, 
                parse_mode=ParseMode.MARKDOWN
            )
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик callback кнопок"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        data = query.data
        
        if data.startswith("mood_score_"):
            # Обработка выбора оценки настроения
            score = float(data.split("_")[-1])
            
            # Обновляем состояние пользователя
            if user_id not in self._user_states:
                self._user_states[user_id] = {}
            
            self._user_states[user_id].update({
                "action": "waiting_mood_text",
                "mood_score": score
            })
            
            await query.edit_message_text(
                f"✅ Оценка настроения: {score}/10\n\n"
                f"📝 Теперь опишите ваш день и настроение:\n"
                f"Что происходило? Как вы себя чувствуете? Что повлияло на настроение?"
            )
        
        elif data == "analytics":
            await self.analytics_command(update, context)
        
        elif data == "recommendations":
            await self.recommendations_command(update, context)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик текстовых сообщений"""
        user_id = update.effective_user.id
        message_text = update.message.text
        
        # Обработка кнопок клавиатуры
        if message_text == "📝 Записать настроение":
            await self.mood_command(update, context)
            return
        elif message_text == "📊 Моя статистика":
            await self.stats_command(update, context)
            return
        elif message_text == "💡 Рекомендации":
            await self.recommendations_command(update, context)
            return
        elif message_text == "📈 Аналитика":
            await self.analytics_command(update, context)
            return
        elif message_text == "❓ Помощь":
            await self.help_command(update, context)
            return
        
        # Обработка состояний пользователя
        user_state = self._user_states.get(user_id, {})
        
        if user_state.get("action") == "waiting_mood_text":
            # Пользователь отправил описание настроения
            mood_score = user_state.get("mood_score")
            mood_text = message_text
            
            if len(mood_text) < 10:
                await update.message.reply_text(
                    "📝 Пожалуйста, опишите ваше настроение подробнее (минимум 10 символов).\n\n"
                    "Например: что происходило в течение дня, что повлияло на настроение, как вы себя чувствуете."
                )
                return
            
            # Сохраняем запись в БД
            await self._save_mood_entry(update, user_id, mood_score, mood_text)
            
            # Очищаем состояние
            if user_id in self._user_states:
                del self._user_states[user_id]
        else:
            # Обычное сообщение
            await update.message.reply_text(
                "🤔 Не понимаю команду. Используйте /help для справки или кнопки меню."
            )
    
    async def _save_mood_entry(self, update: Update, user_id: int, mood_score: float, mood_text: str):
        """Сохранение записи настроения"""
        try:
            with SessionLocal() as db:
                # Создаем запись настроения
                entry_data = MoodEntryCreate(
                    mood_score=mood_score,
                    mood_text=mood_text,
                    entry_date=datetime.now()
                )
                
                mood_entry = mood_entry_crud.create(db, entry_data, user_id)
                
                # Увеличиваем счетчик у пользователя
                user_crud.increment_mood_entries(db, user_id)
                
                # Отправляем подтверждение
                await update.message.reply_text(
                    f"✅ *Запись сохранена!*\n\n"
                    f"📊 Оценка: {mood_score}/10\n"
                    f"📝 Описание: {mood_text[:100]}{'...' if len(mood_text) > 100 else ''}\n\n"
                    f"🧠 Анализирую с помощью ИИ...",
                    parse_mode=ParseMode.MARKDOWN
                )
                
                # Запускаем AI анализ асинхронно
                analysis = await mood_analyzer.analyze_and_save(db, mood_entry)
                
                if analysis:
                    # Отправляем результат анализа
                    analysis_text = f"""
🧠 *Анализ завершен!*

🎭 Доминирующая эмоция: {analysis.dominant_emotion or 'неопределено'}
📈 Тональность: {self._get_sentiment_emoji(analysis.sentiment_label)} {analysis.sentiment_label or 'нейтральная'}

💡 *Рекомендация:*
{analysis.recommendations or 'Продолжайте вести дневник для лучшего анализа'}

🔍 *Инсайт:*
{analysis.insights or 'Ваши записи помогают лучше понять эмоциональные паттерны'}
"""
                    await update.message.reply_text(analysis_text, parse_mode=ParseMode.MARKDOWN)
                else:
                    await update.message.reply_text(
                        "⚠️ Анализ временно недоступен, но запись сохранена.\n"
                        "Используйте /stats для просмотра статистики."
                    )
                
        except Exception as e:
            logger.error(f"Ошибка сохранения записи: {e}")
            await update.message.reply_text(
                "❌ Произошла ошибка при сохранении записи. Попробуйте позже."
            )
    
    def _get_sentiment_emoji(self, sentiment: str) -> str:
        """Получить эмодзи для тональности"""
        emoji_map = {
            "positive": "😊",
            "neutral": "😐", 
            "negative": "😔"
        }
        return emoji_map.get(sentiment, "🤔")
    
    async def run_polling(self):
        """Запуск бота в режиме polling"""
        if not self.application:
            logger.error("❌ Приложение бота не инициализировано")
            return
        
        logger.info("🤖 Запускаю Telegram Bot в режиме polling...")
        
        try:
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling(
                drop_pending_updates=True,
                allowed_updates=Update.ALL_TYPES
            )
            
            logger.info("✅ Telegram Bot запущен и готов к работе!")
            
            # Держим бота работающим
            import signal
            stop_event = asyncio.Event()
            
            def signal_handler():
                logger.info("🛑 Получен сигнал остановки")
                stop_event.set()
            
            # Регистрируем обработчик сигналов
            for sig in [signal.SIGINT, signal.SIGTERM]:
                signal.signal(sig, lambda s, f: signal_handler())
            
            await stop_event.wait()
            
        except Exception as e:
            logger.error(f"❌ Ошибка запуска бота: {e}")
            import traceback
            logger.error(f"Полная трассировка: {traceback.format_exc()}")
            raise
        finally:
            logger.info("🔄 Останавливаю бота...")
            try:
                await self.application.stop()
                await self.application.shutdown()
            except Exception as e:
                logger.error(f"Ошибка при остановке: {e}")


# Создаем экземпляр бота
mood_bot = MoodDiaryBot()