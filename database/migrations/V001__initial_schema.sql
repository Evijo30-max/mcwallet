/*
===============================================================================
 Dailymobile / Multi-Currency Wallet
 V001__initial_schema.sql

 OBJECTIF
 --------
 Première version du schéma PostgreSQL de la plateforme.

 Cette migration contient UNIQUEMENT :
    - extensions nécessaires
    - tables
    - contraintes
    - index
    - quelques fonctions/triggers techniques

 Elle ne contient PAS :
    - utilisateurs réels
    - devises réelles
    - partenaires réels
    - données de production

 PRINCIPES FINANCIERS
 --------------------
 1. Le Ledger est la source de vérité financière.
 2. Les montants financiers ne sont jamais stockés en FLOAT.
 3. Une écriture Ledger validée ne doit jamais être modifiée.
 4. Les opérations financières ont une référence unique.
 5. Les dépôts/retraits sont simulés dans la V1.
 6. Une conversion ne peut concerner que deux wallets du même utilisateur.
 7. Les frais sont conservés séparément.
 8. Les paramètres utilisés lors d'une opération doivent être historisés.

 PostgreSQL
===============================================================================
*/


/*
===============================================================================
 0. EXTENSIONS
===============================================================================
*/

CREATE EXTENSION IF NOT EXISTS pgcrypto;


/*
===============================================================================
 1. USERS
===============================================================================

 Représente les utilisateurs particuliers de la plateforme.

 Exemple :
    Alice
    Bob
    etc.

 Le mot de passe est TOUJOURS stocké sous forme de hash.
===============================================================================
*/

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    first_name VARCHAR(100) NOT NULL,
    last_name  VARCHAR(100) NOT NULL,

    email VARCHAR(255),
    phone VARCHAR(30),

    password_hash TEXT NOT NULL,

    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT users_status_check
        CHECK (
            status IN (
                'ACTIVE',
                'SUSPENDED',
                'CLOSED'
            )
        )
);

CREATE UNIQUE INDEX users_email_unique_idx
    ON users (LOWER(email))
    WHERE email IS NOT NULL;

CREATE UNIQUE INDEX users_phone_unique_idx
    ON users (phone)
    WHERE phone IS NOT NULL;


/*
===============================================================================
 2. COUNTRIES
===============================================================================

 Référentiel des pays.

 Exemple :
    CM = Cameroun
    US = États-Unis
    ES = Espagne

 Nous utilisons le code ISO alpha-2.
===============================================================================
*/

CREATE TABLE countries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    code VARCHAR(2) NOT NULL,
    name VARCHAR(100) NOT NULL,

    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',

    CONSTRAINT countries_code_unique
        UNIQUE (code),

    CONSTRAINT countries_code_uppercase_check
        CHECK (code = UPPER(code)),

    CONSTRAINT countries_status_check
        CHECK (
            status IN (
                'ACTIVE',
                'INACTIVE'
            )
        )
);


/*
===============================================================================
 3. CURRENCIES
===============================================================================

 Référentiel des devises supportées.

 Exemple V1 :
    USD
    EUR
    XAF

 decimal_places indique le nombre de décimales normalement utilisables
 pour la devise.

 Exemple :
    USD = 2
    EUR = 2
    XAF = 0
===============================================================================
*/

CREATE TABLE currencies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    code VARCHAR(3) NOT NULL,
    name VARCHAR(100) NOT NULL,
    symbol VARCHAR(10) NOT NULL,

    decimal_places SMALLINT NOT NULL,

    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT currencies_code_unique
        UNIQUE (code),

    CONSTRAINT currencies_code_uppercase_check
        CHECK (code = UPPER(code)),

    CONSTRAINT currencies_decimal_places_check
        CHECK (
            decimal_places BETWEEN 0 AND 6
        ),

    CONSTRAINT currencies_status_check
        CHECK (
            status IN (
                'ACTIVE',
                'INACTIVE'
            )
        )
);


/*
===============================================================================
 4. PAYMENT METHODS
===============================================================================

 Définit COMMENT un utilisateur effectue une opération.

 Exemples :
    MOBILE_MONEY
    BANK_TRANSFER
    BANK_DEPOSIT

 Attention :
    PAYMENT_METHOD != PARTNER

 Exemple :
    Partner = Orange Money
    Payment method = Mobile Money
===============================================================================
*/

CREATE TABLE payment_methods (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    name VARCHAR(100) NOT NULL,
    type VARCHAR(30) NOT NULL,

    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT payment_methods_type_check
        CHECK (
            type IN (
                'MOBILE_MONEY',
                'BANK_TRANSFER',
                'BANK_DEPOSIT',
                'OTHER'
            )
        ),

    CONSTRAINT payment_methods_status_check
        CHECK (
            status IN (
                'ACTIVE',
                'INACTIVE'
            )
        )
);


/*
===============================================================================
 5. PARTNERS
===============================================================================

 Entreprises/services partenaires utilisés pour les dépôts/retraits.

 Exemples :
    Orange Money
    MTN Mobile Money
    UBA
    Express Union
===============================================================================
*/

CREATE TABLE partners (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    name VARCHAR(150) NOT NULL,
    type VARCHAR(30) NOT NULL,

    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT partners_type_check
        CHECK (
            type IN (
                'MOBILE_MONEY',
                'BANK',
                'PAYMENT_PROVIDER',
                'OTHER'
            )
        ),

    CONSTRAINT partners_status_check
        CHECK (
            status IN (
                'ACTIVE',
                'INACTIVE'
            )
        )
);


/*
===============================================================================
 6. WALLETS
===============================================================================

 Un wallet représente le portefeuille d'un utilisateur dans UNE devise.

 Exemple :

    Alice
      ├── USD Wallet
      ├── EUR Wallet
      └── XAF Wallet

 Règle fondamentale :

    Un utilisateur ne peut avoir qu'un seul wallet pour une devise donnée.

 Donc :

    UNIQUE(user_id, currency_id)
===============================================================================
*/

CREATE TABLE wallets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    user_id UUID NOT NULL,
    currency_id UUID NOT NULL,

    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT wallets_user_fk
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE RESTRICT,

    CONSTRAINT wallets_currency_fk
        FOREIGN KEY (currency_id)
        REFERENCES currencies(id)
        ON DELETE RESTRICT,

    CONSTRAINT wallets_user_currency_unique
        UNIQUE (user_id, currency_id),

    CONSTRAINT wallets_status_check
        CHECK (
            status IN (
                'ACTIVE',
                'SUSPENDED',
                'CLOSED'
            )
        )
);

CREATE INDEX wallets_user_idx
    ON wallets (user_id);

CREATE INDEX wallets_currency_idx
    ON wallets (currency_id);


/*
===============================================================================
 7. LEDGER ACCOUNTS
===============================================================================

 IMPORTANT :
    Cette table représente les comptes comptables internes du système.

 Types possibles :

    USER_WALLET
    PLATFORM_BANK
    PLATFORM_FEES
    FX_CLEARING

 Exemple :

    Alice USD
        -> USER_WALLET
        -> currency = USD
        -> wallet_id = Alice USD wallet

    Compte bancaire plateforme USD
        -> PLATFORM_BANK
        -> currency = USD
        -> wallet_id = NULL

 Le wallet_id est NULL pour les comptes appartenant à la plateforme.
===============================================================================
*/

CREATE TABLE ledger_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    wallet_id UUID,
    currency_id UUID NOT NULL,

    account_type VARCHAR(30) NOT NULL,

    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT ledger_accounts_wallet_fk
        FOREIGN KEY (wallet_id)
        REFERENCES wallets(id)
        ON DELETE RESTRICT,

    CONSTRAINT ledger_accounts_currency_fk
        FOREIGN KEY (currency_id)
        REFERENCES currencies(id)
        ON DELETE RESTRICT,

    CONSTRAINT ledger_accounts_account_type_check
        CHECK (
            account_type IN (
                'USER_WALLET',
                'PLATFORM_BANK',
                'PLATFORM_FEES',
                'FX_CLEARING'
            )
        ),

    CONSTRAINT ledger_accounts_status_check
        CHECK (
            status IN (
                'ACTIVE',
                'INACTIVE'
            )
        ),

    /*
     Un compte USER_WALLET doit obligatoirement être lié à un wallet.
     Les comptes plateforme ne doivent PAS être liés à un wallet.
    */
    CONSTRAINT ledger_accounts_wallet_type_consistency_check
        CHECK (
            (
                account_type = 'USER_WALLET'
                AND wallet_id IS NOT NULL
            )
            OR
            (
                account_type <> 'USER_WALLET'
                AND wallet_id IS NULL
            )
        )
);

CREATE UNIQUE INDEX ledger_accounts_wallet_unique_idx
    ON ledger_accounts (wallet_id)
    WHERE wallet_id IS NOT NULL;

CREATE INDEX ledger_accounts_currency_idx
    ON ledger_accounts (currency_id);

CREATE INDEX ledger_accounts_type_idx
    ON ledger_accounts (account_type);


/*
===============================================================================
 8. LEDGER TRANSACTIONS
===============================================================================

 Représente un événement financier.

 Exemples :

    DEPOSIT
    WITHDRAWAL
    CONVERSION
    FEE
    ADJUSTMENT

 Une transaction contient une ou plusieurs écritures Ledger.
===============================================================================
*/

CREATE TABLE ledger_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    reference VARCHAR(50) NOT NULL UNIQUE,

    transaction_type VARCHAR(30) NOT NULL,

    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    posted_at TIMESTAMPTZ,

    CONSTRAINT ledger_transactions_type_check
        CHECK (
            transaction_type IN (
                'DEPOSIT',
                'WITHDRAWAL',
                'CONVERSION',
                'FEE',
                'ADJUSTMENT'
            )
        ),

    CONSTRAINT ledger_transactions_status_check
        CHECK (
            status IN (
                'PENDING',
                'POSTED',
                'REVERSED',
                'FAILED'
            )
        ),

    /*
     Une transaction POSTED doit avoir une date de posting.
    */
    CONSTRAINT ledger_transactions_posted_at_check
        CHECK (
            status <> 'POSTED'
            OR posted_at IS NOT NULL
        )
);

CREATE INDEX ledger_transactions_type_idx
    ON ledger_transactions (transaction_type);

CREATE INDEX ledger_transactions_status_idx
    ON ledger_transactions (status);

CREATE INDEX ledger_transactions_created_at_idx
    ON ledger_transactions (created_at);


/*
===============================================================================
 9. LEDGER ENTRIES
===============================================================================

 Les écritures individuelles d'une transaction.

 Une entrée est :

    DEBIT
    ou
    CREDIT

 Le montant reste TOUJOURS positif.

 Exemple :

    amount = 500
    entry_type = CREDIT

 et non :

    amount = -500

 IMPORTANT :
    Une écriture POSTED ne doit plus être modifiée par l'application.

 Cette règle sera renforcée côté backend et éventuellement par des triggers
 lorsque nous construirons le système financier complet.
===============================================================================
*/

CREATE TABLE ledger_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    transaction_id UUID NOT NULL,
    ledger_account_id UUID NOT NULL,
    currency_id UUID NOT NULL,

    entry_type VARCHAR(10) NOT NULL,

    amount NUMERIC(30, 8) NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT ledger_entries_transaction_fk
        FOREIGN KEY (transaction_id)
        REFERENCES ledger_transactions(id)
        ON DELETE RESTRICT,

    CONSTRAINT ledger_entries_account_fk
        FOREIGN KEY (ledger_account_id)
        REFERENCES ledger_accounts(id)
        ON DELETE RESTRICT,

    CONSTRAINT ledger_entries_currency_fk
        FOREIGN KEY (currency_id)
        REFERENCES currencies(id)
        ON DELETE RESTRICT,

    CONSTRAINT ledger_entries_type_check
        CHECK (
            entry_type IN (
                'DEBIT',
                'CREDIT'
            )
        ),

    CONSTRAINT ledger_entries_amount_positive_check
        CHECK (
            amount > 0
        )
);

CREATE INDEX ledger_entries_transaction_idx
    ON ledger_entries (transaction_id);

CREATE INDEX ledger_entries_account_idx
    ON ledger_entries (ledger_account_id);

CREATE INDEX ledger_entries_currency_idx
    ON ledger_entries (currency_id);


/*
===============================================================================
 10. RESERVATIONS
===============================================================================

 Une réservation rend temporairement une partie du solde indisponible.

 Exemple :

    Alice possède 500 USD.

    Elle demande un retrait de 100 USD.

    Nous réservons 100 USD avant d'exécuter le retrait.

 Une réservation concerne actuellement :

    - un retrait
 OU
    - une conversion

 Jamais les deux.

===============================================================================
*/

CREATE TABLE reservations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    wallet_id UUID NOT NULL,

    withdrawal_id UUID,
    conversion_id UUID,

    amount NUMERIC(30, 8) NOT NULL,

    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMPTZ NOT NULL,

    released_at TIMESTAMPTZ,
    consumed_at TIMESTAMPTZ,

    CONSTRAINT reservations_wallet_fk
        FOREIGN KEY (wallet_id)
        REFERENCES wallets(id)
        ON DELETE RESTRICT,

    CONSTRAINT reservations_amount_positive_check
        CHECK (
            amount > 0
        ),

    CONSTRAINT reservations_status_check
        CHECK (
            status IN (
                'ACTIVE',
                'CONSUMED',
                'RELEASED',
                'EXPIRED'
            )
        ),

    /*
     EXACTEMENT une opération doit être associée.

     withdrawal_id OU conversion_id
    */
    CONSTRAINT reservations_operation_xor_check
        CHECK (
            (
                withdrawal_id IS NOT NULL
                AND conversion_id IS NULL
            )
            OR
            (
                withdrawal_id IS NULL
                AND conversion_id IS NOT NULL
            )
        )
);

CREATE INDEX reservations_wallet_idx
    ON reservations (wallet_id);

CREATE INDEX reservations_status_idx
    ON reservations (status);

CREATE INDEX reservations_expires_at_idx
    ON reservations (expires_at);


/*
===============================================================================
 11. DEPOSITS
===============================================================================

 Un dépôt représente l'entrée de fonds externes vers un wallet.

 V1 :
    Les dépôts sont simulés.

 IMPORTANT :
    Un dépôt crédite UNE devise.

 Si un jour nous permettons :

    EUR payé -> wallet XAF

 nous créerons un flux composé ou un mécanisme spécifique.

 Nous ne mélangeons pas cela avec le concept simple de DEPOSIT dans V1.
===============================================================================
*/

CREATE TABLE deposits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    reference VARCHAR(50) NOT NULL UNIQUE,

    user_id UUID NOT NULL,
    wallet_id UUID NOT NULL,

    partner_id UUID NOT NULL,
    payment_method_id UUID NOT NULL,

    amount NUMERIC(30, 8) NOT NULL,
    currency_id UUID NOT NULL,

    fee_amount NUMERIC(30, 8) NOT NULL DEFAULT 0,
    fee_mode VARCHAR(20) NOT NULL DEFAULT 'EXCLUDED',

    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMPTZ,

    CONSTRAINT deposits_user_fk
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE RESTRICT,

    CONSTRAINT deposits_wallet_fk
        FOREIGN KEY (wallet_id)
        REFERENCES wallets(id)
        ON DELETE RESTRICT,

    CONSTRAINT deposits_partner_fk
        FOREIGN KEY (partner_id)
        REFERENCES partners(id)
        ON DELETE RESTRICT,

    CONSTRAINT deposits_payment_method_fk
        FOREIGN KEY (payment_method_id)
        REFERENCES payment_methods(id)
        ON DELETE RESTRICT,

    CONSTRAINT deposits_currency_fk
        FOREIGN KEY (currency_id)
        REFERENCES currencies(id)
        ON DELETE RESTRICT,

    CONSTRAINT deposits_amount_positive_check
        CHECK (
            amount > 0
        ),

    CONSTRAINT deposits_fee_positive_check
        CHECK (
            fee_amount >= 0
        ),

    CONSTRAINT deposits_fee_mode_check
        CHECK (
            fee_mode IN (
                'INCLUDED',
                'EXCLUDED'
            )
        ),

    CONSTRAINT deposits_status_check
        CHECK (
            status IN (
                'PENDING',
                'UNDER_REVIEW',
                'APPROVED',
                'REJECTED',
                'CANCELLED'
            )
        )
);

CREATE INDEX deposits_user_idx
    ON deposits (user_id);

CREATE INDEX deposits_wallet_idx
    ON deposits (wallet_id);

CREATE INDEX deposits_status_idx
    ON deposits (status);

CREATE INDEX deposits_created_at_idx
    ON deposits (created_at);


/*
===============================================================================
 12. DEPOSIT PROOFS
===============================================================================

 Justificatifs envoyés pour un dépôt.

 Exemple :
    reçu bancaire
    capture
    document justificatif
===============================================================================
*/

CREATE TABLE deposit_proofs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    deposit_id UUID NOT NULL,

    file_reference TEXT NOT NULL,
    file_type VARCHAR(50),

    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',

    uploaded_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    verified_at TIMESTAMPTZ,

    CONSTRAINT deposit_proofs_deposit_fk
        FOREIGN KEY (deposit_id)
        REFERENCES deposits(id)
        ON DELETE RESTRICT,

    CONSTRAINT deposit_proofs_status_check
        CHECK (
            status IN (
                'PENDING',
                'VERIFIED',
                'REJECTED'
            )
        )
);

CREATE INDEX deposit_proofs_deposit_idx
    ON deposit_proofs (deposit_id);


/*
===============================================================================
 13. WITHDRAWALS
===============================================================================

 Représente une demande de retrait.

 Exemple :

    Alice possède 274400 XAF.

    Elle demande :
        100000 XAF

    Frais :
        1000 XAF

    Selon fee_mode :
        montant débité = 101000
        bénéficiaire = 100000

===============================================================================
*/

CREATE TABLE withdrawals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    reference VARCHAR(50) NOT NULL UNIQUE,

    user_id UUID NOT NULL,
    wallet_id UUID NOT NULL,

    partner_id UUID NOT NULL,
    payment_method_id UUID NOT NULL,

    amount NUMERIC(30, 8) NOT NULL,
    currency_id UUID NOT NULL,

    fee_amount NUMERIC(30, 8) NOT NULL DEFAULT 0,
    fee_mode VARCHAR(20) NOT NULL DEFAULT 'EXCLUDED',

    debited_amount NUMERIC(30, 8) NOT NULL,
    recipient_amount NUMERIC(30, 8) NOT NULL,

    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMPTZ,

    CONSTRAINT withdrawals_user_fk
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE RESTRICT,

    CONSTRAINT withdrawals_wallet_fk
        FOREIGN KEY (wallet_id)
        REFERENCES wallets(id)
        ON DELETE RESTRICT,

    CONSTRAINT withdrawals_partner_fk
        FOREIGN KEY (partner_id)
        REFERENCES partners(id)
        ON DELETE RESTRICT,

    CONSTRAINT withdrawals_payment_method_fk
        FOREIGN KEY (payment_method_id)
        REFERENCES payment_methods(id)
        ON DELETE RESTRICT,

    CONSTRAINT withdrawals_currency_fk
        FOREIGN KEY (currency_id)
        REFERENCES currencies(id)
        ON DELETE RESTRICT,

    CONSTRAINT withdrawals_amount_positive_check
        CHECK (
            amount > 0
        ),

    CONSTRAINT withdrawals_fee_positive_check
        CHECK (
            fee_amount >= 0
        ),

    CONSTRAINT withdrawals_debited_positive_check
        CHECK (
            debited_amount > 0
        ),

    CONSTRAINT withdrawals_recipient_positive_check
        CHECK (
            recipient_amount > 0
        ),

    CONSTRAINT withdrawals_fee_mode_check
        CHECK (
            fee_mode IN (
                'INCLUDED',
                'EXCLUDED'
            )
        ),

    CONSTRAINT withdrawals_status_check
        CHECK (
            status IN (
                'PENDING',
                'PROCESSING',
                'COMPLETED',
                'REJECTED',
                'CANCELLED',
                'FAILED'
            )
        )
);

CREATE INDEX withdrawals_user_idx
    ON withdrawals (user_id);

CREATE INDEX withdrawals_wallet_idx
    ON withdrawals (wallet_id);

CREATE INDEX withdrawals_status_idx
    ON withdrawals (status);

CREATE INDEX withdrawals_created_at_idx
    ON withdrawals (created_at);


/*
===============================================================================
 14. WITHDRAWAL DESTINATIONS
===============================================================================

 Destination vers laquelle l'argent doit être retiré.

 Nous utilisons JSONB car les informations dépendent du type de destination.

 Exemple Orange Money :

 {
     "provider": "ORANGE_MONEY",
     "phone": "6XXXXXXXX"
 }

 Exemple compte bancaire :

 {
     "bank_name": "UBA",
     "account_number": "...",
     "account_name": "..."
 }

 IMPORTANT :
    Le backend devra valider la structure selon destination_type.
===============================================================================
*/

CREATE TABLE withdrawal_destinations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    withdrawal_id UUID NOT NULL UNIQUE,

    destination_type VARCHAR(30) NOT NULL,

    data JSONB NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT withdrawal_destinations_withdrawal_fk
        FOREIGN KEY (withdrawal_id)
        REFERENCES withdrawals(id)
        ON DELETE RESTRICT,

    CONSTRAINT withdrawal_destinations_type_check
        CHECK (
            destination_type IN (
                'MOBILE_MONEY',
                'BANK_ACCOUNT',
                'OTHER'
            )
        ),

    CONSTRAINT withdrawal_destinations_data_object_check
        CHECK (
            jsonb_typeof(data) = 'object'
        )
);


/*
===============================================================================
 15. FX QUOTES
===============================================================================

 Un FX Quote représente le prix proposé à l'utilisateur pendant une période
 limitée.

 Exemple :

    USD -> XAF

    Market rate:
        560

    Margin:
        2 %

    Customer rate:
        548.80

    Source:
        500 USD

    Destination:
        274400 XAF

 IMPORTANT :
    Les valeurs sont conservées telles quelles pour l'historique.

 Si le taux change demain, ce quote ne change PAS.
===============================================================================
*/

CREATE TABLE fx_quotes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    reference VARCHAR(50) NOT NULL UNIQUE,

    source_currency_id UUID NOT NULL,
    destination_currency_id UUID NOT NULL,

    source_amount NUMERIC(30, 8) NOT NULL,
    converted_amount NUMERIC(30, 8) NOT NULL,

    market_rate NUMERIC(30, 12) NOT NULL,
    customer_rate NUMERIC(30, 12) NOT NULL,

    margin_value NUMERIC(30, 12) NOT NULL DEFAULT 0,
    margin_type VARCHAR(20) NOT NULL DEFAULT 'PERCENTAGE',

    fee_amount NUMERIC(30, 8) NOT NULL DEFAULT 0,
    fee_mode VARCHAR(20) NOT NULL DEFAULT 'EXCLUDED',

    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMPTZ NOT NULL,
    used_at TIMESTAMPTZ,

    CONSTRAINT fx_quotes_source_currency_fk
        FOREIGN KEY (source_currency_id)
        REFERENCES currencies(id)
        ON DELETE RESTRICT,

    CONSTRAINT fx_quotes_destination_currency_fk
        FOREIGN KEY (destination_currency_id)
        REFERENCES currencies(id)
        ON DELETE RESTRICT,

    CONSTRAINT fx_quotes_different_currencies_check
        CHECK (
            source_currency_id <> destination_currency_id
        ),

    CONSTRAINT fx_quotes_source_amount_check
        CHECK (
            source_amount > 0
        ),

    CONSTRAINT fx_quotes_converted_amount_check
        CHECK (
            converted_amount > 0
        ),

    CONSTRAINT fx_quotes_market_rate_check
        CHECK (
            market_rate > 0
        ),

    CONSTRAINT fx_quotes_customer_rate_check
        CHECK (
            customer_rate > 0
        ),

    CONSTRAINT fx_quotes_margin_check
        CHECK (
            margin_value >= 0
        ),

    CONSTRAINT fx_quotes_margin_type_check
        CHECK (
            margin_type IN (
                'PERCENTAGE',
                'FIXED'
            )
        ),

    CONSTRAINT fx_quotes_fee_check
        CHECK (
            fee_amount >= 0
        ),

    CONSTRAINT fx_quotes_fee_mode_check
        CHECK (
            fee_mode IN (
                'INCLUDED',
                'EXCLUDED'
            )
        ),

    CONSTRAINT fx_quotes_status_check
        CHECK (
            status IN (
                'ACTIVE',
                'EXPIRED',
                'USED',
                'CANCELLED'
            )
        )
);

CREATE INDEX fx_quotes_source_currency_idx
    ON fx_quotes (source_currency_id);

CREATE INDEX fx_quotes_destination_currency_idx
    ON fx_quotes (destination_currency_id);

CREATE INDEX fx_quotes_status_idx
    ON fx_quotes (status);

CREATE INDEX fx_quotes_expires_at_idx
    ON fx_quotes (expires_at);


/*
===============================================================================
 16. CONVERSIONS
===============================================================================

 Conversion entre deux wallets appartenant au même utilisateur.

 Exemple :

    Alice USD
       ↓
    500 USD
       ↓
    Conversion
       ↓
    274400 XAF
       ↓
    Alice XAF

 IMPORTANT :
    source_wallet_id et destination_wallet_id doivent être différents.

 La vérification :
    source wallet.user_id = destination wallet.user_id

 sera assurée par la logique transactionnelle du backend.
===============================================================================
*/

CREATE TABLE conversions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    reference VARCHAR(50) NOT NULL UNIQUE,

    user_id UUID NOT NULL,

    source_wallet_id UUID NOT NULL,
    destination_wallet_id UUID NOT NULL,

    fx_quote_id UUID NOT NULL,

    source_amount NUMERIC(30, 8) NOT NULL,
    converted_amount NUMERIC(30, 8) NOT NULL,

    fee_amount NUMERIC(30, 8) NOT NULL DEFAULT 0,
    fee_mode VARCHAR(20) NOT NULL DEFAULT 'EXCLUDED',

    debited_amount NUMERIC(30, 8) NOT NULL,
    destination_amount NUMERIC(30, 8) NOT NULL,

    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMPTZ,

    CONSTRAINT conversions_user_fk
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE RESTRICT,

    CONSTRAINT conversions_source_wallet_fk
        FOREIGN KEY (source_wallet_id)
        REFERENCES wallets(id)
        ON DELETE RESTRICT,

    CONSTRAINT conversions_destination_wallet_fk
        FOREIGN KEY (destination_wallet_id)
        REFERENCES wallets(id)
        ON DELETE RESTRICT,

    CONSTRAINT conversions_fx_quote_fk
        FOREIGN KEY (fx_quote_id)
        REFERENCES fx_quotes(id)
        ON DELETE RESTRICT,

    CONSTRAINT conversions_different_wallets_check
        CHECK (
            source_wallet_id <> destination_wallet_id
        ),

    CONSTRAINT conversions_source_amount_check
        CHECK (
            source_amount > 0
        ),

    CONSTRAINT conversions_converted_amount_check
        CHECK (
            converted_amount > 0
        ),

    CONSTRAINT conversions_fee_check
        CHECK (
            fee_amount >= 0
        ),

    CONSTRAINT conversions_debited_amount_check
        CHECK (
            debited_amount > 0
        ),

    CONSTRAINT conversions_destination_amount_check
        CHECK (
            destination_amount > 0
        ),

    CONSTRAINT conversions_fee_mode_check
        CHECK (
            fee_mode IN (
                'INCLUDED',
                'EXCLUDED'
            )
        ),

    CONSTRAINT conversions_status_check
        CHECK (
            status IN (
                'PENDING',
                'PROCESSING',
                'COMPLETED',
                'REJECTED',
                'CANCELLED',
                'FAILED'
            )
        )
);

CREATE INDEX conversions_user_idx
    ON conversions (user_id);

CREATE INDEX conversions_source_wallet_idx
    ON conversions (source_wallet_id);

CREATE INDEX conversions_destination_wallet_idx
    ON conversions (destination_wallet_id);

CREATE INDEX conversions_status_idx
    ON conversions (status);


/*
===============================================================================
 17. PARTNER COUNTRIES
===============================================================================

 Relation N:N :

    PARTNER <-> COUNTRY

 Exemple :

    Orange Money <-> Cameroon
    Orange Money <-> autre pays éventuellement

===============================================================================
*/

CREATE TABLE partner_countries (
    partner_id UUID NOT NULL,
    country_id UUID NOT NULL,

    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (partner_id, country_id),

    CONSTRAINT partner_countries_partner_fk
        FOREIGN KEY (partner_id)
        REFERENCES partners(id)
        ON DELETE RESTRICT,

    CONSTRAINT partner_countries_country_fk
        FOREIGN KEY (country_id)
        REFERENCES countries(id)
        ON DELETE RESTRICT,

    CONSTRAINT partner_countries_status_check
        CHECK (
            status IN (
                'ACTIVE',
                'INACTIVE'
            )
        )
);


/*
===============================================================================
 18. PARTNER CURRENCIES
===============================================================================

 Indique quelles devises un partenaire peut gérer.

 Exemple :

    Orange Money
       XAF
       deposit = TRUE
       withdrawal = TRUE

===============================================================================
*/

CREATE TABLE partner_currencies (
    partner_id UUID NOT NULL,
    currency_id UUID NOT NULL,

    deposit_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    withdrawal_enabled BOOLEAN NOT NULL DEFAULT FALSE,

    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (partner_id, currency_id),

    CONSTRAINT partner_currencies_partner_fk
        FOREIGN KEY (partner_id)
        REFERENCES partners(id)
        ON DELETE RESTRICT,

    CONSTRAINT partner_currencies_currency_fk
        FOREIGN KEY (currency_id)
        REFERENCES currencies(id)
        ON DELETE RESTRICT,

    CONSTRAINT partner_currencies_status_check
        CHECK (
            status IN (
                'ACTIVE',
                'INACTIVE'
            )
        )
);


/*
===============================================================================
 19. PARTNER PAYMENT METHODS
===============================================================================

 Relation :

    PARTNER <-> PAYMENT_METHOD

 Permet de déterminer si une combinaison est utilisable pour :

    dépôt
    retrait
===============================================================================
*/

CREATE TABLE partner_payment_methods (
    partner_id UUID NOT NULL,
    payment_method_id UUID NOT NULL,

    deposit_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    withdrawal_enabled BOOLEAN NOT NULL DEFAULT FALSE,

    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (partner_id, payment_method_id),

    CONSTRAINT partner_payment_methods_partner_fk
        FOREIGN KEY (partner_id)
        REFERENCES partners(id)
        ON DELETE RESTRICT,

    CONSTRAINT partner_payment_methods_method_fk
        FOREIGN KEY (payment_method_id)
        REFERENCES payment_methods(id)
        ON DELETE RESTRICT,

    CONSTRAINT partner_payment_methods_status_check
        CHECK (
            status IN (
                'ACTIVE',
                'INACTIVE'
            )
        )
);


/*
===============================================================================
 20. PAYMENT INSTRUCTIONS
===============================================================================

 Instructions affichées à l'utilisateur pour effectuer un dépôt.

 Exemple :

    Méthode :
        BANK_DEPOSIT

    Partenaire :
        UBA

    Devise :
        USD

    Instructions :
        Déposer sur le compte bancaire XYZ.

 IMPORTANT :
    Une instruction peut être modifiée plus tard depuis le Dashboard.

 Les dépôts historiques doivent conserver les informations nécessaires
 utilisées au moment de leur création.
===============================================================================
*/

CREATE TABLE payment_instructions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    partner_id UUID NOT NULL,
    payment_method_id UUID NOT NULL,
    currency_id UUID NOT NULL,
    country_id UUID,

    title VARCHAR(150) NOT NULL,
    instructions TEXT NOT NULL,

    account_reference TEXT,

    valid_from TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    valid_until TIMESTAMPTZ,

    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT payment_instructions_partner_fk
        FOREIGN KEY (partner_id)
        REFERENCES partners(id)
        ON DELETE RESTRICT,

    CONSTRAINT payment_instructions_method_fk
        FOREIGN KEY (payment_method_id)
        REFERENCES payment_methods(id)
        ON DELETE RESTRICT,

    CONSTRAINT payment_instructions_currency_fk
        FOREIGN KEY (currency_id)
        REFERENCES currencies(id)
        ON DELETE RESTRICT,

    CONSTRAINT payment_instructions_country_fk
        FOREIGN KEY (country_id)
        REFERENCES countries(id)
        ON DELETE RESTRICT,

    CONSTRAINT payment_instructions_status_check
        CHECK (
            status IN (
                'ACTIVE',
                'INACTIVE'
            )
        ),

    CONSTRAINT payment_instructions_validity_check
        CHECK (
            valid_until IS NULL
            OR valid_until > valid_from
        )
);

CREATE INDEX payment_instructions_lookup_idx
    ON payment_instructions (
        partner_id,
        payment_method_id,
        currency_id,
        country_id
    );


/*
===============================================================================
 21. FEE RULES
===============================================================================

 Règles de calcul des frais.

 Exemple :

    WITHDRAWAL
    XAF
    1 %

 ou :

    CONVERSION
    USD -> XAF
    0.5 %

 priority permet de déterminer quelle règle gagne lorsqu'il existe plusieurs
 règles applicables.

===============================================================================
*/

CREATE TABLE fee_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    operation_type VARCHAR(30) NOT NULL,

    source_currency_id UUID,
    destination_currency_id UUID,

    calculation_type VARCHAR(20) NOT NULL,

    value NUMERIC(30, 12) NOT NULL,

    minimum_fee NUMERIC(30, 8),
    maximum_fee NUMERIC(30, 8),

    fee_mode VARCHAR(20) NOT NULL DEFAULT 'EXCLUDED',

    priority INTEGER NOT NULL DEFAULT 100,

    valid_from TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    valid_until TIMESTAMPTZ,

    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fee_rules_source_currency_fk
        FOREIGN KEY (source_currency_id)
        REFERENCES currencies(id)
        ON DELETE RESTRICT,

    CONSTRAINT fee_rules_destination_currency_fk
        FOREIGN KEY (destination_currency_id)
        REFERENCES currencies(id)
        ON DELETE RESTRICT,

    CONSTRAINT fee_rules_operation_type_check
        CHECK (
            operation_type IN (
                'DEPOSIT',
                'WITHDRAWAL',
                'CONVERSION'
            )
        ),

    CONSTRAINT fee_rules_calculation_type_check
        CHECK (
            calculation_type IN (
                'PERCENTAGE',
                'FIXED'
            )
        ),

    CONSTRAINT fee_rules_value_check
        CHECK (
            value >= 0
        ),

    CONSTRAINT fee_rules_minimum_check
        CHECK (
            minimum_fee IS NULL
            OR minimum_fee >= 0
        ),

    CONSTRAINT fee_rules_maximum_check
        CHECK (
            maximum_fee IS NULL
            OR maximum_fee >= 0
        ),

    CONSTRAINT fee_rules_min_max_check
        CHECK (
            minimum_fee IS NULL
            OR maximum_fee IS NULL
            OR minimum_fee <= maximum_fee
        ),

    CONSTRAINT fee_rules_priority_check
        CHECK (
            priority >= 0
        ),

    CONSTRAINT fee_rules_fee_mode_check
        CHECK (
            fee_mode IN (
                'INCLUDED',
                'EXCLUDED'
            )
        ),

    CONSTRAINT fee_rules_status_check
        CHECK (
            status IN (
                'ACTIVE',
                'INACTIVE'
            )
        ),

    CONSTRAINT fee_rules_validity_check
        CHECK (
            valid_until IS NULL
            OR valid_until > valid_from
        )
);

CREATE INDEX fee_rules_lookup_idx
    ON fee_rules (
        operation_type,
        source_currency_id,
        destination_currency_id,
        status,
        priority
    );


/*
===============================================================================
 22. FX RULES
===============================================================================

 Règles utilisées par le moteur de conversion.

 Exemple :

    USD -> XAF

    margin_type = PERCENTAGE
    margin_value = 2

 Cela signifie une marge de 2 % selon notre stratégie FX.

 IMPORTANT :
    Cette table contient la configuration.

    FX_QUOTES contient le snapshot réellement présenté à l'utilisateur.

===============================================================================
*/

CREATE TABLE fx_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    source_currency_id UUID NOT NULL,
    destination_currency_id UUID NOT NULL,

    margin_type VARCHAR(20) NOT NULL,
    margin_value NUMERIC(30, 12) NOT NULL,

    priority INTEGER NOT NULL DEFAULT 100,

    valid_from TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    valid_until TIMESTAMPTZ,

    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fx_rules_source_currency_fk
        FOREIGN KEY (source_currency_id)
        REFERENCES currencies(id)
        ON DELETE RESTRICT,

    CONSTRAINT fx_rules_destination_currency_fk
        FOREIGN KEY (destination_currency_id)
        REFERENCES currencies(id)
        ON DELETE RESTRICT,

    CONSTRAINT fx_rules_different_currencies_check
        CHECK (
            source_currency_id <> destination_currency_id
        ),

    CONSTRAINT fx_rules_margin_type_check
        CHECK (
            margin_type IN (
                'PERCENTAGE',
                'FIXED'
            )
        ),

    CONSTRAINT fx_rules_margin_value_check
        CHECK (
            margin_value >= 0
        ),

    CONSTRAINT fx_rules_priority_check
        CHECK (
            priority >= 0
        ),

    CONSTRAINT fx_rules_status_check
        CHECK (
            status IN (
                'ACTIVE',
                'INACTIVE'
            )
        ),

    CONSTRAINT fx_rules_validity_check
        CHECK (
            valid_until IS NULL
            OR valid_until > valid_from
        )
);

CREATE INDEX fx_rules_lookup_idx
    ON fx_rules (
        source_currency_id,
        destination_currency_id,
        status,
        priority
    );


/*
===============================================================================
 23. LIMIT RULES
===============================================================================

 Limites opérationnelles.

 Exemple :

    WITHDRAWAL
    XAF
    minimum = 1000
    maximum = 1000000

===============================================================================
*/

CREATE TABLE limit_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    operation_type VARCHAR(30) NOT NULL,
    currency_id UUID NOT NULL,

    minimum_amount NUMERIC(30, 8),
    maximum_amount NUMERIC(30, 8),

    priority INTEGER NOT NULL DEFAULT 100,

    valid_from TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    valid_until TIMESTAMPTZ,

    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT limit_rules_currency_fk
        FOREIGN KEY (currency_id)
        REFERENCES currencies(id)
        ON DELETE RESTRICT,

    CONSTRAINT limit_rules_operation_type_check
        CHECK (
            operation_type IN (
                'DEPOSIT',
                'WITHDRAWAL',
                'CONVERSION'
            )
        ),

    CONSTRAINT limit_rules_minimum_check
        CHECK (
            minimum_amount IS NULL
            OR minimum_amount >= 0
        ),

    CONSTRAINT limit_rules_maximum_check
        CHECK (
            maximum_amount IS NULL
            OR maximum_amount >= 0
        ),

    CONSTRAINT limit_rules_min_max_check
        CHECK (
            minimum_amount IS NULL
            OR maximum_amount IS NULL
            OR minimum_amount <= maximum_amount
        ),

    CONSTRAINT limit_rules_priority_check
        CHECK (
            priority >= 0
        ),

    CONSTRAINT limit_rules_status_check
        CHECK (
            status IN (
                'ACTIVE',
                'INACTIVE'
            )
        ),

    CONSTRAINT limit_rules_validity_check
        CHECK (
            valid_until IS NULL
            OR valid_until > valid_from
        )
);

CREATE INDEX limit_rules_lookup_idx
    ON limit_rules (
        operation_type,
        currency_id,
        status,
        priority
    );


/*
===============================================================================
 24. AUDIT LOGS
===============================================================================

 Historique des actions importantes.

 Exemples :

    ADMIN a modifié une règle de frais.
    ADMIN a approuvé un dépôt.
    ADMIN a désactivé un partenaire.
    ADMIN a modifié un taux/marge.

 old_value et new_value sont conservés sous forme JSONB.

 actor_id et entity_id ne sont volontairement PAS des FK classiques car
 l'audit peut concerner différentes sortes d'entités.

===============================================================================
*/

CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    actor_type VARCHAR(30) NOT NULL,
    actor_id UUID,

    action VARCHAR(100) NOT NULL,

    entity_type VARCHAR(50) NOT NULL,
    entity_id UUID,

    old_value JSONB,
    new_value JSONB,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT audit_logs_actor_type_check
        CHECK (
            actor_type IN (
                'USER',
                'ADMIN',
                'SYSTEM'
            )
        )
);

CREATE INDEX audit_logs_actor_idx
    ON audit_logs (actor_type, actor_id);

CREATE INDEX audit_logs_entity_idx
    ON audit_logs (entity_type, entity_id);

CREATE INDEX audit_logs_created_at_idx
    ON audit_logs (created_at);


/*
===============================================================================
 25. INDEXES SUPPLÉMENTAIRES
===============================================================================

 Index destinés aux recherches fréquentes.

===============================================================================
*/

CREATE INDEX ledger_accounts_status_idx
    ON ledger_accounts (status);

CREATE INDEX ledger_entries_created_at_idx
    ON ledger_entries (created_at);

CREATE INDEX deposits_reference_idx
    ON deposits (reference);

CREATE INDEX withdrawals_reference_idx
    ON withdrawals (reference);

CREATE INDEX conversions_reference_idx
    ON conversions (reference);


/*
===============================================================================
 26. COMMENTAIRES DE DOCUMENTATION
===============================================================================

 Ces commentaires apparaissent dans PostgreSQL et permettent de documenter
 directement la base.

===============================================================================
*/

COMMENT ON TABLE wallets IS
    'Portefeuille utilisateur indépendant par devise.';

COMMENT ON TABLE ledger_accounts IS
    'Comptes internes utilisés par le Ledger financier.';

COMMENT ON TABLE ledger_transactions IS
    'Événements financiers composés d''une ou plusieurs écritures Ledger.';

COMMENT ON TABLE ledger_entries IS
    'Écritures financières immuables après posting.';

COMMENT ON TABLE reservations IS
    'Montants temporairement bloqués pour une opération en cours.';

COMMENT ON TABLE deposits IS
    'Demandes de dépôt externe vers un wallet utilisateur.';

COMMENT ON TABLE withdrawals IS
    'Demandes de retrait depuis un wallet utilisateur.';

COMMENT ON TABLE conversions IS
    'Conversions entre deux wallets du même utilisateur.';

COMMENT ON TABLE fx_quotes IS
    'Snapshot d''un taux de change proposé à un utilisateur.';

COMMENT ON TABLE fee_rules IS
    'Configuration des règles de frais.';

COMMENT ON TABLE fx_rules IS
    'Configuration des marges du moteur de change.';

COMMENT ON TABLE limit_rules IS
    'Configuration des limites opérationnelles.';


/*
===============================================================================
 FIN V001
===============================================================================
*/