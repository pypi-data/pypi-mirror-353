import pymysql

'''
提供简单的方法，更快捷地操作数据库

'''



class MySQL(object):
    def __init__(self, host: str, user: str, password: str, database: str, port=3306, charset='utf8', debug: bool=False) -> None:
        """
        Man! What can I say? SQL out!
        :param host: MySQL server host
        :param port: default value 3306
        :param user: username
        :param password: password
        :param database: targeted database name
        :param charset: default value utf8
        :param debug: if True, raise error instead of just printing out
        """
        self.debug = debug
        self.AND = '_AND'
        self.OR = '_OR'

        try:
            self.conn = pymysql.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database,
                charset=charset
            )
        except Exception as e:
            if self.debug is True:
                raise e
            else:
                print(e)
        finally:
            self.cursor = self.conn.cursor()
            print('MySQL connection established')


    def __del__(self):
        self.closeconnect()
        print('MySQL connection closed')


    def closeconnect(self) -> None:
        self.closecursor()
        self.conn.close()


    def closecursor(self) -> None:
        self.cursor.close()


    def refreshcursor(self) -> None:
        self.cursor = self.conn.cursor()


    def getcolumnname(self, table) -> tuple:
        """
        Get each column name.
        :param table: target table
        :return: a tuple including each column name in order.
        """
        self.cursor.execute("DESCRIBE {}".format(table))
        columns = self.cursor.fetchall()
        res = []
        for column in columns:
            res.append(column[0])
        res = tuple(res)
        return res


    def fetchone(self) -> tuple:
        """
        Fetch an element from cursor in order to fetch the next one.
        :return: a tuple including just one element.
        """
        try:
            return self.cursor.fetchone()
        except Exception as e:
            if self.debug is True:
                raise e
            else:
                print(e)


    def fetchmany(self, size: int) -> tuple:
        """
        Fetch some elements from cursor in order.
        :param size: size of fetch
        :return: a tuple
        """
        res = []
        try:
            for _ in range(size):
                fetch = self.cursor.fetchone()
                if fetch is not None:
                    res.append(fetch)
                else:
                    break
        except Exception as e:
            if self.debug is True:
                raise e
            else:
                print(e)
        res = tuple(res)
        return res


    def fetchall(self) -> tuple:
        """
        Fetch all elements from cursor in order.
        :return: a tuple
        """
        try:
            res = self.cursor.fetchall()
            return res
        except Exception as e:
            if self.debug is True:
                raise e
            else:
                print(e)


    def select(self, table, wcolumn=None, wvalue=None, orderincolumn=None, limit=None, orderby='ASC') -> bool:
        """
        Just select items from table.
        :param table: targeted table
        :param wcolumn: targeted column
        :param wvalue: value to column
        :param orderby: DESC or ASC
        :param limit: range of rows
        :return: boolean
        """
        sql = "SELECT * FROM {}".format(table)
        if orderincolumn is not None:
            sql += " ORDER BY {} {}".format(orderincolumn, orderby)

        if wcolumn is not None and wvalue is not None:
            sql += " WHERE `{}` = '{}'".format(wcolumn, wvalue)

        if limit is not None:
            sql += " LIMIT {}".format(limit)

        self.cursor.execute(sql)


    def selectitems(self, table, wcolumn=None, wvalue=None, orderincolumn=None, limit=None, orderby='ASC') -> tuple:
        """
        Fetch items from table.
        :param table: targeted table
        :param wcolumn: targeted column
        :param wvalue: value to column
        :param orderby: DESC or ASC
        :param limit: range of rows
        :return: a tuple including some items
        """
        sql = "SELECT * FROM {}".format(table)
        if orderincolumn is not None:
            sql += " ORDER BY {} {}".format(orderincolumn, orderby)

        if wcolumn is not None and wvalue is not None:
            sql += " WHERE `{}` = '{}'".format(wcolumn, wvalue)

        if limit is not None:
            sql += " LIMIT {}".format(limit)

        self.cursor.execute(sql)
        return self.cursor.fetchall()


    def insert(self, table, column: tuple | list, value: tuple | list, fill=None) -> bool:
        """
        Insert items into table.
        :param table: targeted table
        :param column: targeted column
        :param value: values to column
        :param fill: the other column will be filled with this
        :return: boolean
        """
        if isinstance(column, (tuple, list)) and isinstance(value, (tuple, list)):
            for i in value:
                print(i)
                if not isinstance(i, (tuple, list)):
                    if fill is not None:
                        column = list(column)
                        value = list(value)
                        all_columns = self.getcolumnname(table)
                        count = 1
                        for c in all_columns:
                            if c not in column:
                                column.insert(count, c)
                                value.insert(count, fill)
                            count += 1

                    columns = '(' + ','.join(column) + ')'
                    values = []
                    for item in value:
                        values.append(str(item))
                    values = tuple(values)
                    sql = "INSERT INTO {} {} VALUES {}".format(table, columns, values)
                    # print(sql)

                    try:
                        self.cursor.execute(sql)
                        self.conn.commit()
                        return True
                    except Exception as e:
                        self.conn.rollback()
                        if self.debug is True:
                            raise e
                        else:
                            print(e)
                            return False
                else:
                    if fill is not None:
                        column = list(column)
                        value = list(i)
                        all_columns = self.getcolumnname(table)
                        count = 1
                        for c in all_columns:
                            if c not in column:
                                column.insert(count, c)
                                value.insert(count, fill)
                            count += 1

                    columns = '(' + ','.join(column) + ')'
                    values = []
                    for item in i:
                        values.append(str(item))
                    values = tuple(values)
                    sql = "INSERT INTO {} {} VALUES {}".format(table, columns, values)
                    # print(sql)

                    try:
                        self.cursor.execute(sql)
                    except Exception as e:
                        if self.debug is True:
                            raise e
                        else:
                            print(e)
            try:
                self.conn.commit()
                return True
            except Exception as e:
                self.conn.rollback()
                if self.debug is True:
                    raise e
                else:
                    print(e)
                    return False


        else:
            if self.debug is True:
                raise AttributeError('column or value is not a tuple or list')
            else:
                return False


    def update(self, table, column: tuple | list, value: tuple | list, wcolumn=None, wvalue=None) -> bool:
        """
        Update items from table.
        :param table: targeted table
        :param column: column to be updated
        :param value: value to be updated
        :param wcolumn: targeted column
        :param wvalue: targeted value
        :return: boolean
        """
        sql = "UPDATE {} SET".format(table)
        if isinstance(column, (tuple, list)) and isinstance(value, (tuple, list)):
            if len(column) == len(value):
                try:
                    count = 1
                    len_column = len(column)
                    for c, v in zip(column, value):
                        if count != len_column:
                            sql += " {} = '{}',".format(c, v)
                        else:
                            sql += " {} = '{}'".format(c, v)
                        count += 1
                    sql += " WHERE `{}` = '{}'".format(wcolumn, wvalue)
                    self.cursor.execute(sql)
                    self.conn.commit()
                except Exception as e:
                    if self.debug is True:
                        raise e
                    else:
                        print(e)
                        return False
            else:
                if self.debug is True:
                    raise pymysql.err.OperationalError("Column count doesn't match value count")
                else:
                    print("Column count doesn't match value count")
                    return False
        else:
            if self.debug is True:
                raise AttributeError('column or value is not a tuple or list')
            else:
                return False


    def delete(self, table, wcolumn: tuple | list=None, wvalue: tuple | list=None, logic: tuple | list=None) -> bool:
        """

        :param table: targeted table
        :param wcolumn: column of targeted row to be deleted
        :param wvalue: value to wcolumn
        :param logic: The logical relationships between conditions
        :return: boolean
        """
        sql = "DELETE FROM {} WHERE".format(table)
        if isinstance(logic, (tuple, list)):
            logic = list(logic)
            temp_logic = []
            for i in logic:
                if i == 'AND' or i == 'and' or i == self.AND:
                    temp_logic.append('AND')
                elif i == 'OR' or i == 'or' or i == self.OR:
                    temp_logic.append('OR')
                else:
                    if self.debug is True:
                        raise TypeError(f"'{i}' can be recognized. Do you want 'AND' or 'OR'?")
                    else:
                        print(f"'{i}' can be recognized. Do you want 'AND' or 'OR'?")
            logic = temp_logic

            if len(logic) != 0:
                logic.append('0')
            else:
                if self.debug is True:
                    raise TypeError("No element in tuple or list 'logic'")
                else:
                    print("No element in tuple or list 'logic'")
                    return False

            if isinstance(wcolumn, (tuple, list)) and isinstance(wvalue, (tuple, list)):
                if len(wcolumn) == len(wvalue) == len(logic):
                    count = 1
                    length = len(wcolumn)
                    for c, v, l in zip(wcolumn, wvalue, logic):
                        if count != length:
                            sql += " `{}` = '{}' {}".format(c, v, l)
                        else:
                            sql += " `{}` = '{}'".format(c, v)
                        count += 1
                elif len(wcolumn) == len(wvalue) != len(logic):
                    if self.debug is True:
                        raise TypeError("The number of elements in 'logic' is not right. Be sure that the number is one less than wcolumn and wvalue")
                    else:
                        print("The number of elements in 'logic' is not right. Be sure that the number is one less than wcolumn and wvalue")
                        return False
                else:
                    if self.debug is True:
                        raise pymysql.err.OperationalError("wcolumn count doesn't match wvalue count")
                    else:
                        print("wcolumn count doesn't match wvalue count")
                        return False
                try:
                    self.cursor.execute(sql)
                    self.conn.commit()
                    return True
                except Exception as e:
                    if self.debug is True:
                        raise e
                    else:
                        print(e)
                        return False

            else:
                if self.debug is True:
                    raise AttributeError('column or value is not a tuple or list')
                else:
                    print("column or value is not a tuple or list")
                    return False
        else:
            if isinstance(wcolumn, (tuple, list)) and isinstance(wvalue, (tuple, list)):
                if len(wcolumn) == len(wvalue):
                    count = 1
                    length = len(wcolumn)
                    for c, v in zip(wcolumn, wvalue):
                        if count != length:
                            sql += " `{}` = '{}' AND".format(c, v)
                        else:
                            sql += " `{}` = '{}'".format(c, v)
                        count += 1
                else:
                    if self.debug is True:
                        raise pymysql.err.OperationalError("wcolumn count doesn't match wvalue count")
                    else:
                        print("wcolumn count doesn't match wvalue count")
                        return False
                try:
                    self.cursor.execute(sql)
                    self.conn.commit()
                    return True
                except Exception as e:
                    if self.debug is True:
                        raise e
                    else:
                        print(e)
                        return False

            else:
                if self.debug is True:
                    raise AttributeError('column or value is not a tuple or list')
                else:
                    print("column or value is not a tuple or list")
                    return False