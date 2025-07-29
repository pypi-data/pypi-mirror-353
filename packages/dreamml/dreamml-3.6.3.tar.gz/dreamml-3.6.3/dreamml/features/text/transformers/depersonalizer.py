import pymorphy2
from typing import List
from tqdm import tqdm
import re
from sklearn.base import BaseEstimator, TransformerMixin


class Depersonalizer(TransformerMixin, BaseEstimator):
    """Depersonalizer is a scikit-learn transformer that anonymizes text data by removing or masking sensitive information.

    Sensitive entities such as emails, login names, company names (preceded by specific prepositions), numbers, site links, and personal names and surnames are identified and replaced with tokens.
    """

    def __init__(self, rus_names_dict: dict, verbose: bool = True):
        """Initialize the Depersonalizer.

        Args:
            rus_names_dict (dict): Dictionary containing Russian names and surnames.
            verbose (bool, optional): If True, shows progress bars during transformation. Defaults to True.
        """
        self.rus_names_dict = rus_names_dict
        self.verbose = verbose
        self.__parsers_init__()

    def fit(self, X, y=None):
        """Fit the transformer.

        This transformer does not require fitting; it simply returns itself.

        Args:
            X: Input data.
            y: Target values (unused).

        Returns:
            Depersonalizer: The fitted transformer.
        """
        return self

    def transform(self, X):
        """Transform the data by anonymizing text.

        Args:
            X: Iterable of text documents to be anonymized.

        Returns:
            list of str: Anonymized text documents.
        """
        if self.verbose:
            X = tqdm(X, "Depersonalization")
        return [self.make_it_anonim(str(doc)) for doc in X]

    def __parsers_init__(self):
        """Initialize internal parsers and regex patterns.

        Sets up lists of names, surnames, and compiles various regular expressions used for anonymization.
        """
        self.name_list = set(self.rus_names_dict["names"])
        self.surname_list = set(self.rus_names_dict["surnames"])

        self.pymorphy_parser = pymorphy2.MorphAnalyzer()
        self.name_tags = ["Patr sing", "Surn sing", "Name"]
        self.company_types = [
            "[Аа][Кк][Цц][Ии][Оо][Нн][Ее][Рр][Нн][Оо][Ее] [Оо][Бб][Щщ][Ее][Сс][Тт][Вв][Оо]",
            '[Аа][Кк][Цц][Ии][Оо][Нн][Ее][Рр][Нн][Оо][Ее] [Оо][Бб][Щщ][Ее][Сс][Тт][Вв][Оо] ["][\w+\s]+["]',
            '[Ии][Нн][Дд][Ии][Вв][Ии][Дд][Уу][Аа][Лл][Ьь][Нн][Ыы][Йй] [Пп][Рр][Ее][Дд][Пп][Рр][Ии][Нн][Ии][Мм][Аа][Тт][Ее][Лл][Ьь] ["][\w+\s]+["]',
            '[Оо][Бб][Щщ][Ее][Сс][Тт][Вв][Оо] [Сс] [Оо][Гг][Рр][Аа][Нн][Ии][Чч][Ее][Нн][Нн][Оо][Йй] [Оо][Тт][Вв][Ее][Тт][Сс][Тт][Вв][Ее][Нн][Нн][Оо][Сс][Тт][Ьь][Юю] [Гг][Рр][Уу][Пп][Пп][Аа] [Кк][Оо][Мм][Пп][Аа][Нн][Ии][Йй] ["][\w+\s]+["]',
            '[Оо][Бб][Щщ][Ее][Сс][Тт][Вв][Оо] [Сс] [Оо][Гг][Рр][Аа][Нн][Ии][Чч][Ее][Нн][Нн][Оо][Йй] [Оо][Тт][Вв][Ее][Тт][Сс][Тт][Вв][Ее][Нн][Нн][Оо][Сс][Тт][Ьь][Юю] ["][\w+\s]+["]',
            '[Мм][Ее][Дд][Ии][Аа] [Аа][Гг][Ее][Нн][Тт][Сс][Тт][Вв][Оо] ["][\w+\s]+["]',
            '[Нн][Пп][Оо] ["][\w+\s]+["]',
            '[Нн][Аа][Уу][Чч][Нн][Оо]-[Пп][Рр][Оо][Ии][Зз][Вв][Оо][Дд][Сс][Тт][Вв][Ее][Нн][Нн][Оо][Ее] [Пп][Рр][Ее][Дд][Пп][Рр][Ии][Яя][Тт][Ии][Ее] ["][\w+\s]+["]',
            '[Пп][Кк][Фф] ["][\w+\s]+["]',
            '[Сс][Пп][Ее][Цц][Ии][Аа][Лл][Ии][Зз][Ии][Рр][Оо][Вв][Аа][Нн][Нн][Ыы][Йй] [Зз][Аа][Сс][Тт][Рр][Оо][Йй][Щщ][Ии][Кк] ["][\w+\s]+["]',
            '[Сс][Оо][Вв][Мм][Ее][Сс][Тт][Нн][Оо][Ее] [Пп][Рр][Ее][Дд][Пп][Рр][Ии][Яя][Тт][Ии][Ее] ["][\w+\s]+["]',
        ]
        self.company_types_re = [re.compile(r) for r in self.company_types]

        self.company_abrv = {"ооо", "тоо", "пао", "оао", "ип"}

        self.link_re = re.compile(
            r"""\b((?:https?://)?(?:(?:www\.)?(?:[\da-z\.-]+)\.(?:[a-z]{2,6})|(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)|
                   (?:(?:[0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,7}:|(?:[0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,5}(?::[0-9a-fA-F]{1,4})
                    {1,2}|(?:[0-9a-fA-F]{1,4}:){1,4}(?::[0-9a-fA-F]{1,4}){1,3}|(?:[0-9a-fA-F]{1,4}:){1,3}(?::[0-9a-fA-F]{1,4}){1,4}|(?:[0-9a-fA-F]{1,4}:){1,2}(?::[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:
                    (?:(?::[0-9a-fA-F]{1,4}){1,6})|:(?:(?::[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(?::[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(?:ffff(?::0{1,4}){0,1}:){0,1}(?:(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9])
                    {0,1}[0-9])\.){3,3}(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])|(?:[0-9a-fA-F]{1,4}:){1,4}:(?:(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(?:25[0-5]|
                    (?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])))(?::[0-9]{1,4}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])?(?:/[\w\.-]*)*/?)\b"""
        )

        self.login_re = re.compile(r"\w+(?:-[A-Za-z]+)+")
        self.number_re = re.compile(r"\d+")
        self.subtoken_re = re.compile("[а-яА-ЯйёЙЁ]+")
        self.abr_names_1 = re.compile(r"(\b|\s)([А-Я]\.)(| )([А-Я]\w+)")
        self.abr_names_2 = re.compile(r"([А-Я]\w+\ )([А-Я]\.)(| )")

    def __company_name_processing(self, text: List[str]) -> List[str]:
        """Process and anonymize company names in the text.

        Args:
            text (List[str]): List of tokens from the text.

        Returns:
            List[str]: Tokens with company names replaced by 'COMPANY_TOKEN'.
        """
        for tind, token in enumerate(text[1:]):
            if text[tind].lower() in self.company_abrv:
                text[tind + 1] = "COMPANY_TOKEN"
        return text

    def __site_links_processing(self, token: str) -> str:
        """Process and anonymize site links in the token.

        Args:
            token (str): A single token from the text.

        Returns:
            str: 'URL_TOKEN' if the token matches a link pattern, otherwise the original token.
        """
        if self.link_re.search(token):
            return "URL_TOKEN"
        else:
            return token

    @staticmethod
    def __email_processing(token: str) -> str:
        """Process and anonymize email addresses in the token.

        Args:
            token (str): A single token from the text.

        Returns:
            str: 'EMAIL_TOKEN' if the token contains an email indicator, otherwise the original token.
        """
        email_detector = "@"
        if email_detector in token:
            return "EMAIL_TOKEN"
        else:
            return token

    def __login_processing(self, token: str) -> str:
        """Process and anonymize login names in the token.

        Args:
            token (str): A single token from the text.

        Returns:
            str: 'LOGIN_TOKEN' if the token matches a login pattern, otherwise the original token.
        """
        if self.login_re.search(token):
            return "LOGIN_TOKEN"
        else:
            return token

    def __number_processing(self, token: str) -> str:
        """Process and anonymize numbers in the token.

        Args:
            token (str): A single token from the text.

        Returns:
            str: 'NUM_TOKEN' if the token contains digits, otherwise the original token.
        """
        if self.number_re.findall(token):
            return "NUM_TOKEN"
        else:
            return token

    def __name_processing(self, token: str) -> str:
        """Process and anonymize names and surnames in the token.

        Args:
            token (str): A single token from the text.

        Returns:
            str: 'NAME_TOKEN' if the token is identified as a name or surname, otherwise the original token.
        """
        original_token = token

        subtokens = self.subtoken_re.findall(token)
        processed_tokens = []

        for subtoken in subtokens:
            if subtoken.lower() in self.name_list:
                processed_tokens.append(" NAME_TOKEN ")

            elif subtoken.lower() in self.surname_list:
                processed_tokens.append(" NAME_TOKEN ")

            token_normal_form = self.pymorphy_parser.parse(subtoken.lower())[0].normal_form

            if token_normal_form in self.name_list:
                processed_tokens.append(" NAME_TOKEN ")
            elif token_normal_form in self.surname_list:
                processed_tokens.append(" NAME_TOKEN ")

            token_tag = str(self.pymorphy_parser.parse(subtoken.lower())[0].tag)
            for tag in self.name_tags:
                if tag in token_tag:
                    processed_tokens.append(" NAME_TOKEN ")
            else:
                processed_tokens.append(subtoken)

        for tind, subtoken in enumerate(subtokens):
            original_token = original_token.replace(subtoken, processed_tokens[tind])

        return original_token

    def make_it_anonim(self, text: str) -> str:
        """Anonymize the input text by replacing sensitive information with tokens.

        Args:
            text (str): The text to be anonymized.

        Returns:
            str: The anonymized text.
        """
        abr_names = self.abr_names_1.findall(text)
        if abr_names:
            for name in abr_names:
                name = "".join(name).strip()
                text = text.replace(name, " NAME_TOKEN ")
        abr_names = self.abr_names_2.findall(text)
        if abr_names:
            for name in abr_names:
                name = "".join(name).strip()
                text = text.replace(name, " NAME_TOKEN ")

        text = text.replace("-", " ")
        text = re.sub("[Ии][Сс][Уу]", "интеллектуальная система управления", text)
        text = re.sub("[Аа][Рр][Мм]", "СБЕРАРМ", text)
        text = re.sub("[Ии][Нн][Нн]", "индивидуальный номер налогоплательщика", text)
        text = re.sub(r"\s+", " ", text)

        text = self.company_types_re[0].sub(" оао", text)
        for comp_type_re in self.company_types_re[1:]:
            text = comp_type_re.sub(" COMPANY_TOKEN ", text)

        text = text.split()

        text = self.__company_name_processing(text)

        for tind, token in enumerate(text):
            text[tind] = self.__site_links_processing(token)
            text[tind] = self.__email_processing(text[tind])
            text[tind] = self.__login_processing(text[tind])
            text[tind] = self.__number_processing(text[tind])
            text[tind] = self.__name_processing(text[tind])

        return " ".join(text)