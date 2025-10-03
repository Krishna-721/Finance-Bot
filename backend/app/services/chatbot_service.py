from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional,Dict
from datetime import datetime, timedelta
import re
from app.models.chat import ChatMessage
from app.models.user import User
from app.models.transaction import Transaction, TransactionType

class ChatbotService:
    """Chatbot Service: handles intent recognition and response generation"""
    @staticmethod
    def process_message(db: Session, user: User, message:str)->Dict[str,str]:
        """Method to process user message and generate repsonse"""
        message_lower = message.lower().strip()

        intent,response = ChatbotService._generate_response(db,user,message_lower)
        chat_message=ChatMessage(
            user_id=user.id,
            user_message=message,
            bot_response=response,
            intent=intent
        )
        db.add(chat_message)
        db.commit()

        return{
            "user_message":message,
            "bot_response":response,
            "intent":intent,
            "timestamp":datetime.now()
        }
    
    @staticmethod
    def _generate_response(db: Session, user: User, message: str) -> tuple[str, str]:
        """
        Detect intent and generate response
        Returns: (intent, response)
        """
        
        # Intent 1: Balance/Summary
        if any(word in message for word in ["balance", "summary", "total", "overview"]):
            return ChatbotService._handle_balance(db, user)
        
        # Intent 2: Spending by category
        if "spend" in message or "spent" in message:
            category = ChatbotService._extract_category(message)
            if category:
                return ChatbotService._handle_category_spending(db, user, category)
            else:
                return ChatbotService._handle_total_spending(db, user)
        
        # Intent 3: Income queries
        if "income" in message or "earned" in message or "salary" in message:
            return ChatbotService._handle_income(db, user)
        
        # Intent 4: Recent transactions
        if "recent" in message or "last" in message or "latest" in message:
            return ChatbotService._handle_recent_transactions(db, user)
        
        # Intent 5: Savings advice
        if any(word in message for word in ["save", "saving", "tips", "advice", "recommend"]):
            return ChatbotService._handle_savings_advice(db, user)
        
        # Intent 6: Biggest expense
        if "biggest" in message or "largest" in message or "most expensive" in message:
            return ChatbotService._handle_biggest_expense(db, user)
        
        # Default: Didn't understand
        return ChatbotService._handle_unknown(message)
    
    @staticmethod
    def _extract_category(message: str) -> Optional[str]:
        """
        Extract category from message
        """
        categories = ["food", "rent", "transport", "entertainment", "utilities", 
                     "shopping", "healthcare", "salary", "freelance"]
        
        for category in categories:
            if category in message:
                return category.capitalize()
        return None
    
    @staticmethod
    def _handle_balance(db: Session, user: User) -> tuple[str, str]:
        """Handle balance/summary queries"""
        total_income = db.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user.id,
            Transaction.type == TransactionType.INCOME
        ).scalar() or 0.0
        
        total_expenses = db.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user.id,
            Transaction.type == TransactionType.EXPENSE
        ).scalar() or 0.0
        
        net_balance = total_income - total_expenses
        
        response = (
            f"🧾**Financial Summary**\n\n"
            f"💰 Total Income: ${total_income:,.2f}\n"
            f"💸 Total Expenses: ${total_expenses:,.2f}\n"
            f"𓍝 Net Balance: ${net_balance:,.2f}\n\n"
        )
        
        if net_balance > 0:
            response += f"Great job! You're saving ${net_balance:,.2f}! 🎉"
        elif net_balance < 0:
            response += f"⚠️ You're spending ${abs(net_balance):,.2f} more than you earn. Consider reviewing your expenses."
        else:
            response += "You're breaking even. Try to save a little each month! 💪🏻"
        
        return ("balance_query", response)
    
    @staticmethod
    def _handle_category_spending(db: Session, user: User, category: str) -> tuple[str, str]:
        """Handle spending by specific category"""
        total = db.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user.id,
            Transaction.type == TransactionType.EXPENSE,
            Transaction.category.ilike(f"%{category}%")
        ).scalar() or 0.0
        
        count = db.query(Transaction).filter(
            Transaction.user_id == user.id,
            Transaction.type == TransactionType.EXPENSE,
            Transaction.category.ilike(f"%{category}%")
        ).count()
        
        if count == 0:
            response = f"You haven't recorded any expenses in the '{category}' category yet."
        else:
            avg = total / count
            response = (
                f"📊 **{category} Spending**\n\n"
                f"💸 Total: ${total:,.2f}\n"
                f"📝 Transactions: {count}\n"
                f"📊 Average: ${avg:,.2f} per transaction"
            )
        
        return ("category_spending", response)
    
    @staticmethod
    def _handle_total_spending(db: Session, user: User) -> tuple[str, str]:
        """Handle total spending queries"""
        total_expenses = db.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user.id,
            Transaction.type == TransactionType.EXPENSE
        ).scalar() or 0.0
        
        # Top 3 categories
        top_categories = db.query(
            Transaction.category,
            func.sum(Transaction.amount).label('total')
        ).filter(
            Transaction.user_id == user.id,
            Transaction.type == TransactionType.EXPENSE
        ).group_by(Transaction.category).order_by(func.sum(Transaction.amount).desc()).limit(3).all()
        
        response = f"💸 **Total Expenses: ${total_expenses:,.2f}**\n\n"
        
        if top_categories:
            response += "Top spending categories:\n"
            for i, (category, amount) in enumerate(top_categories, 1):
                percentage = (amount / total_expenses * 100) if total_expenses > 0 else 0
                response += f"{i}. {category}: ${amount:,.2f} ({percentage:.1f}%)\n"
        
        return ("total_spending", response)
    
    @staticmethod
    def _handle_income(db: Session, user: User) -> tuple[str, str]:
        """Handle income queries"""
        total_income = db.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user.id,
            Transaction.type == TransactionType.INCOME
        ).scalar() or 0.0
        
        count = db.query(Transaction).filter(
            Transaction.user_id == user.id,
            Transaction.type == TransactionType.INCOME
        ).count()
        
        response = (
            f"💰 **Income Summary**\n\n"
            f"📈 Total Income: ${total_income:,.2f}\n"
            f"📝 Income Transactions: {count}"
        )
        
        return ("income_query", response)
    
    @staticmethod
    def _handle_recent_transactions(db: Session, user: User) -> tuple[str, str]:
        """Handle recent transactions queries"""
        recent = db.query(Transaction).filter(
            Transaction.user_id == user.id
        ).order_by(Transaction.date.desc()).limit(5).all()
        
        if not recent:
            response = "You don't have any transactions yet. Start adding some!"
        else:
            response = "📋 **Recent Transactions:**\n\n"
            for t in recent:
                emoji = "📈" if t.type == TransactionType.INCOME else "📉"
                response += f"{emoji} ${t.amount:,.2f} - {t.category} ({t.description or 'No description'})\n"
        
        return ("recent_transactions", response)
    
    @staticmethod
    def _handle_savings_advice(db: Session, user: User) -> tuple[str, str]:
        """Handle savings advice queries"""
        total_income = db.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user.id,
            Transaction.type == TransactionType.INCOME
        ).scalar() or 0.0
        
        total_expenses = db.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user.id,
            Transaction.type == TransactionType.EXPENSE
        ).scalar() or 0.0
        
        if total_income == 0:
            return ("savings_advice", "Add some income transactions first so I can give you personalized advice!")
        
        savings_rate = ((total_income - total_expenses) / total_income * 100) if total_income > 0 else 0
        
        response = "💡 **Savings Tips:**\n\n"
        
        if savings_rate >= 20:
            response += f"🌟 Excellent! You're saving {savings_rate:.1f}% of your income. Keep it up!"
        elif savings_rate >= 10:
            response += f"👍 Good job! You're saving {savings_rate:.1f}% of your income. Try to reach 20% for optimal savings."
        elif savings_rate > 0:
            response += f"⚠️ You're saving {savings_rate:.1f}% of your income. Financial experts recommend at least 20%."
        else:
            response += f"🚨 You're spending more than you earn! Consider cutting unnecessary expenses."
        
        # Find biggest expense category
        top_category = db.query(
            Transaction.category,
            func.sum(Transaction.amount).label('total')
        ).filter(
            Transaction.user_id == user.id,
            Transaction.type == TransactionType.EXPENSE
        ).group_by(Transaction.category).order_by(func.sum(Transaction.amount).desc()).first()
        
        if top_category:
            cat_name, cat_total = top_category
            percentage = (cat_total / total_income * 100) if total_income > 0 else 0
            response += f"\n\n💰 Your biggest expense is {cat_name} (${cat_total:,.2f}, {percentage:.1f}% of income). Consider reducing this category to boost savings!"
        
        return ("savings_advice", response)
    
    @staticmethod
    def _handle_biggest_expense(db: Session, user: User) -> tuple[str, str]:
        """Handle biggest expense queries"""
        biggest = db.query(Transaction).filter(
            Transaction.user_id == user.id,
            Transaction.type == TransactionType.EXPENSE
        ).order_by(Transaction.amount.desc()).first()
        
        if not biggest:
            response = "You don't have any expenses recorded yet."
        else:
            response = (
                f"💸 **Your Biggest Expense:**\n\n"
                f"Amount: ${biggest.amount:,.2f}\n"
                f"Category: {biggest.category}\n"
                f"Description: {biggest.description or 'No description'}\n"
                f"Date: {biggest.date.strftime('%Y-%m-%d')}"
            )
        
        return ("biggest_expense", response)
    
    @staticmethod
    def _handle_unknown(message: str) -> tuple[str, str]:
        """Handle unrecognized queries"""
        response = (
            "🤔 I'm not sure I understood that. Here's what I can help you with:\n\n"
            "💰 Ask about your **balance** or **summary**\n"
            "📊 Check **spending** by category (e.g., 'How much did I spend on food?')\n"
            "📈 View your **income**\n"
            "📋 See **recent** transactions\n"
            "💡 Get **savings tips** and advice\n"
            "💸 Find your **biggest expense**\n\n"
            "Try asking me something like: 'What's my balance?' or 'How much did I spend on food?'"
        )
        
        return ("unknown", response)
    
    @staticmethod
    def get_chat_history(db: Session, user: User, limit: int = 20) -> list:
        """
        Get user's chat history
        """
        messages = db.query(ChatMessage).filter(
            ChatMessage.user_id == user.id
        ).order_by(ChatMessage.created_at.desc()).limit(limit).all()
        
        return messages
