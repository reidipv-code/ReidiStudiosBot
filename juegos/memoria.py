def cancelar_timer_memoria(context, user_id):
    if context.job_queue:
        for job in context.job_queue.get_jobs_by_name(f"memoria_{user_id}"):
            job.schedule_removal()


def programar_timer_memoria(context, user_id):
    if not context.job_queue:
        return

    partida = partidas_memoria.get(user_id)
    if not partida or partida.get("deadline") is None:
        return

    cancelar_timer_memoria(context, user_id)
    context.job_queue.run_once(
        timeout_memoria,
        when=max(0, partida["deadline"] - time.monotonic()),
        data={
            "user_id": user_id,
            "ronda": partida["ronda"]
        },
        name=f"memoria_{user_id}"
    )


async def timeout_memoria(context):
    data = context.job.data
    user_id = data["user_id"]
    partida = partidas_memoria.get(user_id)

    if not partida or partida["ronda"] != data["ronda"]:
        return

    restante = partida["deadline"] - time.monotonic()
    if restante > 0:
        programar_timer_memoria(context, user_id)
        return

    try:
        await context.bot.send_message(
            chat_id=partida["chat_id"],
            text="⏰ ¡Se acabó el tiempo!"
        )
    except Exception:
        pass

    await terminar_memoria(context, user_id, gano=False)


async def mostrar_secuencia(context, user_id):
    partida = partidas_memoria.get(user_id)
    if not partida:
        return

    ronda = partida["ronda"]
    cantidad = emojis_por_ronda(ronda)
    emojis = [random.choice(FRUTAS) for _ in range(cantidad)]

    partida["emojis"] = emojis
    partida["deadline"] = None
    partida["tiempo_limite"] = tiempo_memoria(ronda)

    try:
        mensaje = await context.bot.send_message(
            chat_id=partida["chat_id"],
            text=(
                f"🧠 *Ronda {ronda}/50*\n"
                "━━━━━━━━━━━━━━━━━━━\n"
                f"📋 *Memoriza estos {cantidad} emojis:*\n\n"
                f"{' '.join(emojis)}\n\n"
                f"⏱️ Tienes *{partida['tiempo_limite']} segundos*.\n"
                "Responde: `.🍎 🍌 🍇`"
            ),
            parse_mode="Markdown"
        )
    except Exception:
        await terminar_memoria(context, user_id, gano=False)
        return

    if user_id not in partidas_memoria:
        return

    partida["message_id"] = mensaje.message_id
    partida["deadline"] = time.monotonic() + partida["tiempo_limite"]
    programar_timer_memoria(context, user_id)


async def borrar_secuencia(context):
    # Compatibilidad con los trabajos antiguos de eliminación de mensajes.
    data = context.job.data
    try:
        await context.bot.delete_message(
            chat_id=data["chat_id"],
            message_id=data["message_id"]
        )
    except Exception:
        pass


async def responder_memoria(update, context):
    if not update.effective_user or not update.message or not update.message.text:
        return

    user_id = update.effective_user.id
    partida = partidas_memoria.get(user_id)
    if not partida:
        return

    texto = update.message.text.strip()
    if not texto.startswith("."):
        return

    deadline = partida.get("deadline")
    if deadline is None or time.monotonic() >= deadline:
        await update.message.reply_text("⏰ ¡Se acabó el tiempo!")
        await terminar_memoria(context, user_id, gano=False)
        raise ApplicationHandlerStop

    respuesta = texto[1:].strip()
    emojis_usuario = extraer_emojis(respuesta)
    emojis_correctos = partida["emojis"]

    if len(emojis_usuario) != len(emojis_correctos):
        await update.message.reply_text(
            f"❌ Escribiste {len(emojis_usuario)} emojis, "
            f"pero eran {len(emojis_correctos)}."
        )
        raise ApplicationHandlerStop

    aciertos = sum(
        1 for i, emoji in enumerate(emojis_usuario)
        if emoji == emojis_correctos[i]
    )

    if aciertos != len(emojis_correctos):
        resetear_xp(user_id)
        await update.message.reply_text(
            f"❌ ¡Incorrecto! Acertaste {aciertos}/{len(emojis_correctos)}.\n"
            "💔 Has perdido toda la XP de tu barra."
        )
        await terminar_memoria(context, user_id, gano=False)
        raise ApplicationHandlerStop

    cancelar_timer_memoria(context, user_id)
    partida["deadline"] = None
    partida["aciertos"] += 1

    actualizar_tokens(user_id, cantidad_con_bonus_tokens(user_id, 2, "memoria"))
    aplicar_bonus_xp(user_id, 2, "memoria")

    if partida["ronda"] >= 20 and dar_logro(user_id, "memorion"):
        await avisar_logro(context, user_id, "memorion")

    for m_id in sumar_progreso(
        user_id, "memoria_ronda", cantidad=partida["ronda"]
    ):
        await avisar_mision(context, user_id, m_id)

    if partida["ronda"] >= 50:
        await terminar_memoria(context, user_id, gano=True)
        raise ApplicationHandlerStop

    partida["ronda"] += 1
    await update.message.reply_text(
        f"✅ ¡Correcto!\n💰 +2 tokens, ✨ +2 XP\n"
        f"🎯 Ronda {partida['ronda']}..."
    )
    await mostrar_secuencia(context, user_id)
    raise ApplicationHandlerStop


async def revisar_timeouts_memoria(context):
    ahora = time.monotonic()
    for user_id, partida in list(partidas_memoria.items()):
        deadline = partida.get("deadline")
        if deadline is not None and ahora >= deadline:
            await timeout_memoria_manual(context, user_id)


async def timeout_memoria_manual(context, user_id):
    partida = partidas_memoria.get(user_id)
    if not partida or partida.get("deadline") is None:
        return

    if time.monotonic() < partida["deadline"]:
        return

    try:
        await context.bot.send_message(
            chat_id=partida["chat_id"],
            text="⏰ ¡Se acabó el tiempo!"
        )
    except Exception:
        pass

    await terminar_memoria(context, user_id, gano=False)