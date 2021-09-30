import datetime as dt
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.float_format', lambda x: '%.2f' % x)

###GÖREV1###

##2010-2011 yılı içerisindeki veriler#veri setini okuma
df_ = pd.read_excel("online_retail_II.xlsx",
                    sheet_name="Year 2010-2011")

df=df_.copy(),

df.head()


#veri setinin betimsel istatistikleri
df.tail()
df.shape
df.info()
df.describe().T

#veri setinde eksik gözlem var mı # hangi değişkende kaç tane eksik gözlem var

df.isnull().values.any()
df.isnull().sum()

#Eksik gözlemleri çıkar, inplace=True kullan

df.dropna(inplace=True)
df.shape

#eşsiz ürün sayısı

df["StockCode"].nunique()

#hangi üründen kaçar tane var

df["StockCode"].value_counts()

#en çok sipariş edilen 5 ürünü çoktan aza doğru sırala

df.groupby("StockCode").agg({"Quantity":"sum"}).sort_values(by="Quantity",ascending=False)

#faturalardaki 'C' iptal işlemlerini veri setinden çıkart

df = df[~df["Invoice"].str.contains("C", na=False)]
df.shape

#fatura basına elde edilen toplam kazancı ifade eden 'TotalPrice' adında değişken oluştur

df["TotalPrice"] = df["Quantity"] * df["Price"]
df.head()


###GÖREV2###
##RFM metriklerinin hesaplanması

#recency,frequency, monetary tanımlarını yapınız
#müşteri özelinde recency,frequency, monetary metriklerini groupby, agg ve lambda ile hesaplayınız
#hesaplanan metrikleri rfm isimli bir değişkene atayınız
#olusturdugun metriklerin isimlerini recency,frequency, monetary olarak değiştiriniz
#NOTLAR:recency değeri için bugünün tarihi (2011,12,11) olacak ve rfm df' i oluşturduktan sonra veri setini
#"monetary>0" olacak sekilde filtreleyiniz.

df["InvoiceDate"].max()
today_date = dt.datetime(2011, 12, 11)

# recency_invoicedate
# frequency_invoice
# monetary_totalprice

rfm = df.groupby('Customer ID').agg({'InvoiceDate': lambda InvoiceDate: (today_date - InvoiceDate.max()).days,
                                     'Invoice': lambda Invoice: Invoice.nunique(),
                                     'TotalPrice': lambda TotalPrice: TotalPrice.sum()})

rfm.head()
rfm.columns = ['recency', 'frequency', 'monetary']
rfm.describe().T
rfm = rfm[rfm["monetary"] > 0]


###GÖREV3###
##RFM Skorlarının Olusturulması ve tek bir değişkene cevrilmesi

#recency,frequency, monetary metriklerini qcut yardımıyla 1-5 arasında skorlara cevir
#Bu skorları recency_score,frequency_score ve monetary_score olarak kaydet
#recency_score ve frequency_score' u tek bir değişken olarak ifade et ve RFM_SCORE olarak kaydet
#(monetary_score' u dahil etmiyoruz)


rfm["recency_score"] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])

rfm["frequency_score"] = pd.qcut(rfm['frequency'].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])

rfm["monetary_score"] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5])


rfm["RFM_SCORE"] = (rfm['recency_score'].astype(str) +
                    rfm['frequency_score'].astype(str))


###GÖREV4###
##RFM Skorlarının segment olarak tanımlanması
#olusturulan RFM Skorlarının daha açıklanabilir olması için segment tanımlaması yap
#seg_map yardımıyla skorları segmente cevir.

seg_map = {
    r'[1-2][1-2]': 'hibernating',
    r'[1-2][3-4]': 'at_Risk',
    r'[1-2]5': 'cant_loose',
    r'3[1-2]': 'about_to_sleep',
    r'33': 'need_attention',
    r'[3-4][4-5]': 'loyal_customers',
    r'41': 'promising',
    r'51': 'new_customers',
    r'[4-5][2-3]': 'potential_loyalists',
    r'5[4-5]': 'champions'
}

rfm['segment'] = rfm["RFM_SCORE"].replace(seg_map,regex=True)

###GÖREV5###
#Önemli bulduğunuz 3 segmenti seçiniz.Aksiyon kararları ve segment yapıları açısından (ortalama RFM değerleri)
# yorumlayınız



rfm[["segment", "recency", "frequency", "monetary"]].groupby("segment").agg(["mean", "count"])

#CHAMPIONS: en iyi müşteriyi temsil eder. Çıktıda recency ortalaması 6.36 yani en yakın tarihte alışveriş yapan müşteri
#bizim için en iyi olan müşteridir.ortalaması 6,36 olan 663 müşterimiz var ve frequency değeri ort. sı en yüksek olan
#en cok alışveriş yapan, monetary içinde de en yüksek ortalamayı getiren  müşterilerimizi temsil ettiğini söyleyebiliriz
#Müşterimizi ödüllendirebilir, indirim/kampanya fırsatları sunabiliriz.
#AT_RISK: Kaybetmek üzere olduğumuz müşterilerimizdir. Varolanı elimizde tutmak yeni müşteri kazanmaktan daha az
#maliyetli olduğundan müşteriyi elimizde tutmaya çalışmalıyız. kendimizi hatrlatacak mail, mesaj gibi hatırlatma
#mesajları gönderebiliriz, ürünlerimizin reklamlarını, indirim/kampanya gibi fırsatları hatırlatabiliriz.
#need attention: dikkat edilmesi gereken gruptur. Bu müşterilerimizle ilgilenmezsek recency ve Frequency değerleri
#azalacağından riskli gruba yaklaşır.En son  187 kişi ortalama 52 gün 2.33 frekansında 897,63 birim tutarda alışveriş yapmış


#loyal customers sınıfına ait customer ıdleri secerek excel cıktısı al.

rfm[rfm["segment"] == "loyal_customers"]


new_df = pd.DataFrame()
new_df["new_customer_id"] = rfm[rfm["segment"] == "loyal_customers"].index
new_df.head()

new_df.to_excel("loyal_customers.xlsx")