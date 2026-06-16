from src.data_preparation import DataPreparation

prep = DataPreparation("data/train.csv")
df   = prep.prepare()
prep.save(df)

print("\nSample data:")
print(df.head(3))

print("\nNew columns:")
print(df[["sales", "profit", "cost", "profit_margin_%", "quantity", "discount", "shipping_days"]].head(5))