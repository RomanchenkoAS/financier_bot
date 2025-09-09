import pytest
import asyncio
from datetime import datetime
from unittest.mock import MagicMock

from src.telegram.bot import Chat


class TestChatParsing:
    @pytest.fixture
    def chat(self):
        mock_msg = MagicMock()
        mock_msg.bot = MagicMock()
        mock_msg.chat.id = 123456
        return Chat(mock_msg)

    @pytest.mark.asyncio
    async def test_basic_message(self, chat):
        """Test basic message with amount and category only"""
        result = await chat._parse_message("450 кофе")
        
        assert result["amount"] == 450.0
        assert result["category"] == "кофе"
        assert result["comment"] == ""
        assert result["date"] == datetime.now().strftime("%Y-%m-%d")

    @pytest.mark.asyncio
    async def test_message_with_comment_double_quotes(self, chat):
        """Test message with comment in double quotes"""
        result = await chat._parse_message('500 Транспорт "Такси"')
        
        assert result["amount"] == 500.0
        assert result["category"] == "Транспорт"
        assert result["comment"] == "Такси"
        assert result["date"] == datetime.now().strftime("%Y-%m-%d")

    @pytest.mark.asyncio
    async def test_message_with_comment_single_quotes(self, chat):
        """Test message with comment in single quotes"""
        result = await chat._parse_message("500 Транспорт 'Такси'")
        
        assert result["amount"] == 500.0
        assert result["category"] == "Транспорт"
        assert result["comment"] == "Такси"
        assert result["date"] == datetime.now().strftime("%Y-%m-%d")

    @pytest.mark.asyncio
    async def test_message_with_comment_backticks(self, chat):
        """Test message with comment in backticks"""
        result = await chat._parse_message("500 Транспорт `Такси`")
        
        assert result["amount"] == 500.0
        assert result["category"] == "Транспорт"
        assert result["comment"] == "Такси"
        assert result["date"] == datetime.now().strftime("%Y-%m-%d")

    @pytest.mark.asyncio
    async def test_message_with_comment_angle_brackets(self, chat):
        """Test message with comment in angle brackets"""
        result = await chat._parse_message("500 Транспорт <Такси>")
        
        assert result["amount"] == 500.0
        assert result["category"] == "Транспорт"
        assert result["comment"] == "Такси"
        assert result["date"] == datetime.now().strftime("%Y-%m-%d")

    @pytest.mark.asyncio
    async def test_message_with_date_dots(self, chat):
        """Test message with date in format DD.MM.YY"""
        result = await chat._parse_message("450 кофе 01.09.25")
        
        assert result["amount"] == 450.0
        assert result["category"] == "кофе"
        assert result["comment"] == ""
        assert result["date"] == "2025-09-01"

    @pytest.mark.asyncio
    async def test_message_with_date_slashes(self, chat):
        """Test message with date in format DD/MM/YY"""
        result = await chat._parse_message("450 кофе 01/09/25")
        
        assert result["amount"] == 450.0
        assert result["category"] == "кофе"
        assert result["comment"] == ""
        assert result["date"] == "2025-09-01"

    @pytest.mark.asyncio
    async def test_message_with_date_hyphens(self, chat):
        """Test message with date in format DD-MM-YY"""
        result = await chat._parse_message("450 кофе 01-09-25")
        
        assert result["amount"] == 450.0
        assert result["category"] == "кофе"
        assert result["comment"] == ""
        assert result["date"] == "2025-09-01"

    @pytest.mark.asyncio
    async def test_message_with_short_date(self, chat):
        """Test message with short date format DD.MM"""
        result = await chat._parse_message("450 кофе 01.09")
        
        assert result["amount"] == 450.0
        assert result["category"] == "кофе"
        assert result["comment"] == ""
        
        # Should use current year
        current_year = datetime.now().year
        assert result["date"] == f"{current_year}-09-01"

    @pytest.mark.asyncio
    async def test_message_with_date_and_comment(self, chat):
        """Test message with both date and comment"""
        result = await chat._parse_message('450 кофе 01.09.25 "С коллегой"')
        
        assert result["amount"] == 450.0
        assert result["category"] == "кофе"
        assert result["comment"] == "С коллегой"
        assert result["date"] == "2025-09-01"

    @pytest.mark.asyncio
    async def test_message_with_comment_and_date(self, chat):
        """Test message with comment first, then date"""
        result = await chat._parse_message('450 кофе "С коллегой" 01.09.25')
        
        assert result["amount"] == 450.0
        assert result["category"] == "кофе"
        assert result["comment"] == "С коллегой"
        assert result["date"] == "2025-09-01"

    @pytest.mark.asyncio
    async def test_multi_word_category(self, chat):
        """Test message with multi-word category"""
        result = await chat._parse_message("450 кофе с молоком")
        
        assert result["amount"] == 450.0
        assert result["category"] == "кофе с молоком"
        assert result["comment"] == ""
        assert result["date"] == datetime.now().strftime("%Y-%m-%d")

    @pytest.mark.asyncio
    async def test_invalid_amount(self, chat):
        """Test message with invalid amount"""
        with pytest.raises(ValueError, match="Invalid amount"):
            await chat._parse_message("abc кофе")

    @pytest.mark.asyncio
    async def test_invalid_date(self, chat):
        """Test message with invalid date"""
        with pytest.raises(ValueError, match="Invalid date format"):
            await chat._parse_message("450 кофе 32.13.25")

    @pytest.mark.asyncio
    async def test_incomplete_message(self, chat):
        """Test incomplete message with only amount"""
        with pytest.raises(ValueError, match="Message must contain at least amount and category"):
            await chat._parse_message("450")


if __name__ == "__main__":
    pytest.main(["-v", "test.py"])
