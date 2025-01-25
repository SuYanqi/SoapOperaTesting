import pandas as pd


class ExcelUtil:
    @staticmethod
    def to_excel(data_json, writer_filepath, sheet_name):
        """

        @param writer_filepath:
        @type writer_filepath:
        @param sheet_name:
        @type sheet_name:
        @param data_json:
        @type data_json:
        @return:
        @rtype:
        """
        # if not writer_filepath.is_file():
        #     open(writer_filepath, 'w+')
        # Create a Pandas dataframe from some data.
        df = pd.DataFrame(data_json)

        # Create a Pandas Excel writer using XlsxWriter as the engine.
        writer = pd.ExcelWriter(writer_filepath, engine='XlsxWriter')
        # # 解决pandas中to_excel 数据覆盖sheet表问题
        # book = load_workbook(writer_filepath)
        # writer.book = book

        # Convert the dataframe to an XlsxWriter Excel object.
        df.to_excel(writer, sheet_name=sheet_name, index=False, header=True)

        # Get the xlsxwriter objects from the dataframe writer object.
        # workbook = writer.book
        worksheet = writer.sheets[sheet_name]

        # Set the column width.
        worksheet.set_column(0, 0, 50)

        # Close the Pandas Excel writer and output the Excel file.
        writer.save()

