from flask import Blueprint, jsonify, request, abort
from flask_login import current_user, login_required
from sqlalchemy import extract

from models import db
from models.transaction import Transaction

transactions_bp = Blueprint("transactions", __name__)


@transactions_bp.route("/transactions", methods=["GET"])
@login_required
def get_transactions():
    month = request.args.get("month")

    query = Transaction.query.filter_by(user_id=current_user.id)

    if month:
        try:
            month_int = int(month)
            if 1 <= month_int <= 12:
                query = query.filter(extract("month", Transaction.date) == month_int)
        except ValueError:
            pass

    transactions = query.order_by(Transaction.date.desc()).all()

    result = [
        {
            "id": t.id,
            "description": t.description,
            "amount": t.amount,
            "type": t.type,
            "date": t.date.strftime("%d/%m/%Y"),
        }
        for t in transactions
    ]

    return jsonify(result)


@transactions_bp.route("/transactions", methods=["POST"])
@login_required
def add_transaction():
    data = request.get_json(force=True) or {}

    description = (data.get("description") or "").strip()
    amount = data.get("amount")
    ttype = data.get("type")

    if not description or ttype not in ("income", "expense"):
        return jsonify({"error": "Dados de transação inválidos."}), 400

    try:
        amount = float(amount)
    except (TypeError, ValueError):
        return jsonify({"error": "Valor inválido."}), 400

    transaction = Transaction(
        description=description,
        amount=amount,
        type=ttype,
        user_id=current_user.id,
    )

    db.session.add(transaction)
    db.session.commit()

    return jsonify({"message": "ok"}), 201


@transactions_bp.route("/transactions/<int:transaction_id>", methods=["DELETE"])
@login_required
def delete_transaction(transaction_id: int):
    transaction = (
        Transaction.query.filter_by(id=transaction_id, user_id=current_user.id).first()
    )

    if not transaction:
        return abort(404)

    db.session.delete(transaction)
    db.session.commit()

    return jsonify({"message": "ok"}), 200
