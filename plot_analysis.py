import pandas as pd
import matplotlib.pyplot as plt
import base64, os
from PIL import Image
from io import BytesIO
from actionresult import ActionResult


class PlotAnalysis():
    def generate_plots(self, sqlite_engine, query):
        file_name = 'foo.png'
        try:
            connection = sqlite_engine.connect()
            sql_query = pd.read_sql_query(query, connection)
            df = pd.DataFrame(sql_query, columns=['name','price'])
            df['price'] = df['price'].astype('float')
            boxplot = df.boxplot(column=['price'], by='name', grid=False, rot=45) # https://www.statology.org/boxplot-pandas/
            plt.title("Overall fish-price box plot", fontsize=16)
            plt.xlabel('Types of fish available', fontsize=14)
            plt.ylabel('Price of Fish (Min, Median/IQR, Max)', fontsize=14)
            plt.savefig(file_name, format="png", bbox_inches='tight')
            plt.show()
            with open(file_name, "rb") as img:
                data = base64.b64encode(img.read())
                # im = Image.open(BytesIO(base64.b64decode(data)))
                # im.save('image1.png', 'PNG')
            return data
        except Exception as e:
            print(e)
            return str(ActionResult.FAILURE)
        finally:
            if os.path.exists(file_name):
                os.remove(file_name)
