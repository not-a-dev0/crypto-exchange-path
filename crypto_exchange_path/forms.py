from flask_wtf import FlaskForm
from wtforms import (StringField, SubmitField, TextAreaField, SelectField,
                     RadioField, SelectMultipleField)
from wtforms.validators import (DataRequired, Length, ValidationError)
from crypto_exchange_path.config import Params
from crypto_exchange_path.utils_db import (get_active_coins,
                                           get_exch_by_coin,
                                           get_exchange_choices,
                                           get_currency_choices,
                                           get_feedback_topics,
                                           get_coin_by_longname,
                                           get_exch_by_withdrawal_coin)
from crypto_exchange_path.utils import is_number


class SearchForm(FlaskForm):

    currency = SelectField('Currency',
                           choices=get_currency_choices(),
                           validators=[DataRequired()],
                           default='USD')
    orig_loc = SelectField('Origin location',
                           choices=get_exchange_choices())
    orig_coin = StringField('Origin coin')
    orig_amt = StringField('Origin amount')
    dest_loc = SelectField('Destination location',
                           choices=get_exchange_choices(),
                           validators=[DataRequired()])
    dest_coin = StringField('Destination coin')
    connection_type = RadioField('Connections',
                                 choices=Params.CONNECTIONS_CHOICES,
                                 default='2')
    exchanges = SelectMultipleField('Exchanges',
                                    choices=get_exchange_choices('Exchange'),
                                    default=[exch[0] for exch in
                                             get_exchange_choices('Exchange')])
    cep_promos = RadioField('CEP promos',
                            choices=Params.CEP_CHOICES,
                            default='(CEP)')
    default_fee = RadioField('Default fee',
                             choices=Params.TRADE_FEE_CHOICES,
                             default='(Taker)')
    binance_fee = RadioField('Binance fees',
                             choices=[('(BNB)', 'Pay fees in BNB (0.075%)'),
                                      ('(No-BNB)', 'Regular fees (0.1%)')],
                             default='(BNB)')
    search_submit = SubmitField('Search')

    def validate_orig_amt(self, orig_amt):
        if not orig_amt.data:
            raise ValidationError("Please, fill 'Amount'")
        if not is_number(orig_amt.data):
            raise ValidationError("Not a number")
        elif float(orig_amt.data) <= 0:
            raise ValidationError("Amount must be a positive number")

    def validate_orig_coin(self, orig_coin):
        if not orig_coin.data:
            raise ValidationError("Please, fill 'Coin'")
        else:
            coin = get_coin_by_longname(orig_coin.data)
            if coin:
                coin = coin.id
            coins = get_active_coins()
            if coin not in coins:
                raise ValidationError("Unknown coin")

    def validate_orig_loc(self, orig_loc):
        # If 'orig_loc' is 'Wallet', then any coin will be available
        if orig_loc.data == Params.GENERIC_WALLET:
            return
        else:
            coin = get_coin_by_longname(self.orig_coin.data)
            if coin:
                valid_coins = get_active_coins()
                # Only raise error is 'orig_coin' exist
                if coin.id in valid_coins:
                    valid_exchs = get_exch_by_withdrawal_coin(coin.id)
                    if valid_exchs:
                        valid_exchs.add(Params.GENERIC_WALLET)
                    else:
                        valid_exchs = (Params.GENERIC_WALLET)
                    if orig_loc.data not in valid_exchs:
                        raise ValidationError("'{}' not available in '{}'"
                                              .format(coin.id, orig_loc.data))

    def validate_dest_coin(self, dest_coin):
        if not dest_coin.data:
            raise ValidationError("Please, fill 'Coin'")
        else:
            coin = get_coin_by_longname(dest_coin.data)
            if coin:
                coin = coin.id
            coins = get_active_coins()
            if coin not in coins:
                raise ValidationError("Unknown coin")
            elif (dest_coin.data == self.orig_coin.data):
                raise ValidationError("Same origin and destination coin")

    def validate_dest_loc(self, dest_loc):
        # If 'dest_loc' is 'Wallet', then any coin will be available
        if dest_loc.data == Params.GENERIC_WALLET:
            return
        else:
            coin = get_coin_by_longname(self.dest_coin.data)
            if coin:
                valid_coins = get_active_coins()
                # Only raise error is 'dest_coin' exist
                if coin.id in valid_coins:
                    valid_exchs = get_exch_by_coin(coin.id)
                    if valid_exchs:
                        valid_exchs.add(Params.GENERIC_WALLET)
                    else:
                        valid_exchs = (Params.GENERIC_WALLET)
                    if dest_loc.data not in valid_exchs:
                        raise ValidationError("'{}' not available in '{}'"
                                              .format(coin.id, dest_loc.data))


class FeedbackForm(FlaskForm):
    topic = SelectField('Topic',
                        choices=get_feedback_topics())
    subject = StringField('Subject',
                          validators=[Length(max=50), DataRequired()])
    detail = TextAreaField('Detail',
                           validators=[Length(max=200), DataRequired()],
                           filters=[lambda x: x or None])
    feedback_submit = SubmitField('Submit')

    def validate_topic(self, topic):
        topics = Params.FEEDBACK_TOPICS
        if topic.data not in topics:
            raise ValidationError("Please, select a topic")
