#!/usr/bin/python3

# -*- coding: utf-8 -*-

'''
    SmtpChecker.py 

    smtp (postfix) のログから unknown host からの接続回数および
    From: 送信者情報の統計を収集します。
    ファイルを -f オプションで指定しない場合は /var/log/mail.log
    から読み込みます

    出力は標準出力へ、接続回数・IP アドレス・(あれば) 送信者の
    メールアドレスを出力します
'''

# imports
import      re
import      sys
import      getopt
import      fileinput

# _const - 定数
_const                  = dict()

# - 処理するログファイル名のデフォルト - キー:ファイル名のリスト
_const['LOGS']          = ( '/var/log/mail.log' )

# - 識別用のキーワード - キー:コンパイル済の正規表現
_const['POSTFIX']       = re.compile( 'postfix/(|submission/|smtps/)smtpd' )
_const['UNKNOWN']       = re.compile( '(connect|established) from unknown\[' )
_const['REJECT']        = re.compile( 'reject: RCPT from unknown\[' )
_const['ADDRESS']       = re.compile( 'unknown\[(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\]' )
_const['MAILFROM']      = re.compile( 'from=<(\S+)>' )

# - 表示する接続回数の下限のデフォルト 20 回
_const['LIMIT']         = 20

#
# main() - 主処理
#
def         main( argv ) :

    # オプション解析処理を実施する
    option( argv )

    # 主処理を実施する
    output( * proc() )

    return

#
# option() - オプション解析
#
def         option( argv ) :

    # 処理対象のファイルリスト
    logs       = _const['LOGS']

    # 引数があればオプション解析
    if ( len( argv ) == 1 ) :
        pass

    else :
        # 引数の内容を解析する
        try :
            opts, args      = getopt.getopt( argv[1:], "hf:l:" )

            # オプション処理
            for opt, arg in opts :

                # - -h, --help ヘルプ表示
                if opt in ( "-h" ) :
                    raise       getopt.GetoptError

                # - -f, --file ログファイルの指定
                elif opt in ( "-f" ) :
                    _const['LOGS']  = ( arg )

                # - -l, --limit 表示する接続回数の下限
                elif opt in ( "-l" ) :
                    _const['LIMIT'] = int( arg )

                # - その他
                else :
                    raise       getopt.GetoptError

        # help 表示
        except      getopt.GetoptError:
            print ( '{} [-h|--help] [-f|--file <logfile>] [-l|--limit n]'.format( argv[0] ) )
            sys.exit( 2 )

    return

#
# proc() - ログを全行読んで結果リストを返す
#
def     proc() :

    # 結果リスト
    ips     = dict()        # IP アドレスの辞書 - IP:出現回数
    adrs    = dict()        # メールアドレスの辞書 - IP:メールアドレス

    # ログを全行処理する
    for l in fileinput.input( files = _const['LOGS'] ) :

        # postfix のログ行のみが（現在のところ）処理対象
        if not _const['POSTFIX'].search( l ) :
            pass

        # connect/established from unknown 行をチェックする
        elif _const['UNKNOWN'].search( l ) :

            # - IP アドレスを抽出する
            ip      = _const['ADDRESS'].search( l )

            # - IP アドレスが含まれていないれば次へ
            if ip is not None :
                # - 抽出した文字列を取り出す
                s_ip    = ip.group( 1 )

                # - 初めての IP アドレス検出なら回数 1 でリストに追加する
                if not s_ip in ips.keys() :
                    ips[s_ip]     = 1

                # - IP アドレスが二回目以降なら回数を更新する
                else :
                    ips[s_ip]     = ips[s_ip] + 1

        # RCPT from unknown 行をチェックする
        elif _const['REJECT'].search( l ) :

            # - IP アドレスとメールアドレスを抽出する
            ip      = _const['ADDRESS'].search( l )
            adr     = _const['MAILFROM'].search( l )

            # - IP アドレスとメールアドレスが含まれていないれば次へ
            if ip is not None and adr is not None :

                # - 抽出した文字列を取り出す
                s_ip        = ip.group( 1 )
                s_adr       = adr.group( 1 )

                # - 初めての ip アドレスの場合
                if not s_ip in adrs.keys() :
                    adrs[s_ip]      = s_adr

                # - 二回目以降の IP アドレスで違うメールアドレスなら追加
                elif adrs[s_ip].find( s_adr ) is -1:
                    adrs[s_ip]      += ', ' + s_adr

                # - すでにあれば何もしない
                else :
                    pass

        # 他の行はスキップ
        else :
            pass

    return ( ips, adrs )


#
# proc() - ログを全行読んで結果リストを返す
#
def     output( ips, adrs ) :

    # ヘッダの出力
    print( "--- Rejected SMTP access over {} times retry from unknown hosts ---".format( _const['LIMIT'] )  )
    print( "retry : IP address (From:[, ...])" )

    # 回数の多い順に並べ替えてすべてのエントリを出力する
    for ip, c in sorted( ips.items(), key = lambda x : -x[1] ) :
        
        # limit 以上のリトライがあるエントリのみ表示
        if c < _const['LIMIT'] :
            continue

        # メールアドレスがあるなら出力
        elif ip in adrs.keys() :
            adr     = "(" + adrs[ip] + ")"

        else :
            adr     = ""

        # エントリを出力する
        print( "{:5} : {} {}".format( c, ip, adr ) )

    print( '--- ' )

    return 


#
# 主処理呼び出し
#
if __name__ == "__main__": 
    main( sys.argv )
