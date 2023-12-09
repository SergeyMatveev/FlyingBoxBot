FlyingBoxBot is a digital platform that connects senders and couriers.

We have a table 
orders	
order_id	INT, SERIAL
username	VARCHAR(255), NOT NULL
departure_city	VARCHAR(255), NOT NULL
destination_city	VARCHAR(255), NOT NULL
weight	FLOAT, NOT NULL
departure_date	DATE, NOT NULL
user_comment	VARCHAR(255)
created_at	TIMESTAMPTZ, NOT NULL, DEFAULT NOW
is_completed	BOOLEAN, NOT NULL, DEFAULT FALSE
is_package	BOOLEAN, NOT NULL
chat_id	double-precision float, NOT NULL
