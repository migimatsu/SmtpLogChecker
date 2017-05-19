SmtpChecker.py 

smtp (postfix) のログから unknown host からの接続回数および
From: 送信者情報の統計を収集します。
ファイルを -f オプションで指定しない場合は /var/log/mail.log
から読み込みます
出力は標準出力へ、接続回数・IP アドレス・(あれば) 送信者の
メールアドレスを出力します
