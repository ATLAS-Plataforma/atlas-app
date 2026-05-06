import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv

load_dotenv()

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")


def enviar_email_alerta(produto, quantidade, tipo_alerta):

    mensagem = f"""
Produto: {produto}
Alerta: {tipo_alerta}
Quantidade atual: {quantidade}

Ação recomendada:
Realizar reposição do item.

Atlas Estoque
"""

    email = Mail(
        from_email='marianabrito1003@gmail.com',
        to_emails='estoqueatlas05@gmail.com',
        subject=f'Alerta de estoque - {produto}',
        plain_text_content=mensagem
    )

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(email)
        print("Email enviado!", response.status_code)

    except Exception as e:
        print("Erro ao enviar email:", e)

