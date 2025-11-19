"""
Componentes de UI Conversacional para Streamlit

Implementa melhorias visuais baseadas em Extended Thinking e best practices
do Context7 + Streamlit docs.

Author: devAndreJr
Version: 3.0.0
"""

import streamlit as st
import time
from typing import Dict, Any, Generator


class ConversationalUI:
    """Componentes de UI para interface conversacional moderna"""

    # 🎨 AVATARES E EMOJIS
    AVATARS = {
        "user": "👤",
        "caculinha_conversational": "💬",
        "caculinha_analytical": "🤖",
        "caculinha_thinking": "🧠"
    }

    # 🎨 BADGES DE MODO
    MODE_BADGES = {
        "conversational": ("💬 Conversando", "#10a37f"),
        "analytical": ("📊 Analisando", "#5436DA"),
        "thinking": ("🧠 Pensando", "#f59e0b"),
        "une_operation": ("🏭 Operação UNE", "#8b5cf6"),
        "chart": ("📈 Gerando gráfico", "#ec4899")
    }

    @staticmethod
    def render_mode_badge(mode: str) -> None:
        """
        Renderiza badge de modo no topo da resposta

        Args:
            mode: Modo atual (conversational, analytical, etc.)
        """
        if mode in ConversationalUI.MODE_BADGES:
            label, color = ConversationalUI.MODE_BADGES[mode]
            st.markdown(
                f"""
                <div style="
                    display: inline-block;
                    background-color: {color}15;
                    color: {color};
                    border: 1px solid {color}40;
                    border-radius: 12px;
                    padding: 4px 12px;
                    font-size: 12px;
                    font-weight: 600;
                    margin-bottom: 8px;
                ">
                    {label}
                </div>
                """,
                unsafe_allow_html=True
            )

    @staticmethod
    def stream_text(text: str, chunk_size: int = 3) -> Generator[str, None, None]:
        """
        Gera texto em chunks para efeito de streaming/digitação

        Args:
            text: Texto completo a ser streamado
            chunk_size: Número de palavras por chunk

        Yields:
            Chunks de texto
        """
        words = text.split()
        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i + chunk_size]) + " "
            yield chunk
            time.sleep(0.03)  # Velocidade da digitação

    @staticmethod
    def render_conversational_message(
        content: str,
        emotional_tone: str = "neutro",
        show_streaming: bool = True
    ) -> None:
        """
        Renderiza mensagem conversacional com efeito de digitação

        Args:
            content: Conteúdo da mensagem
            emotional_tone: Tom emocional detectado
            show_streaming: Se deve mostrar efeito de digitação
        """
        # Badge de modo conversacional
        ConversationalUI.render_mode_badge("conversational")

        # Card com styling especial para conversacional
        st.markdown(
            """
            <style>
            .conversational-card {
                background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
                border-left: 4px solid #10a37f;
                border-radius: 8px;
                padding: 16px;
                margin: 8px 0;
            }
            .emotional-indicator {
                font-size: 11px;
                color: #8e8ea0;
                margin-bottom: 8px;
                font-style: italic;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        # Indicador de tom emocional (sutil)
        emotional_labels = {
            "frustrado": "😕 Detectei que você pode estar frustrado",
            "curioso": "🤔 Ótima pergunta!",
            "urgente": "⚡ Vou ser rápida",
            "confuso": "💡 Vou explicar melhor",
            "casual": "👋 Tranquilo!",
            "neutro": ""
        }

        if emotional_tone in emotional_labels and emotional_labels[emotional_tone]:
            st.markdown(
                f'<div class="emotional-indicator">{emotional_labels[emotional_tone]}</div>',
                unsafe_allow_html=True
            )

        # Renderizar conteúdo com ou sem streaming
        if show_streaming and len(content) > 50:
            # Streaming apenas para respostas longas
            st.write_stream(ConversationalUI.stream_text(content))
        else:
            st.markdown(content)

    @staticmethod
    def render_analytical_message(
        content: Any,
        content_type: str = "data",
        intent: str = "resposta_simples"
    ) -> None:
        """
        Renderiza mensagem analítica (dados, gráficos, etc.)

        Args:
            content: Conteúdo da resposta (DataFrame, dict, etc.)
            content_type: Tipo de conteúdo (data, chart, text, etc.)
            intent: Intent da query
        """
        # Badge baseado no intent
        mode_map = {
            "une_operation": "une_operation",
            "gerar_grafico": "chart",
            "python_analysis": "analytical",
            "resposta_simples": "analytical"
        }
        badge_mode = mode_map.get(intent, "analytical")
        ConversationalUI.render_mode_badge(badge_mode)

        # Renderizar conteúdo baseado no tipo
        if content_type == "data":
            # DataFrame com configuração otimizada
            if isinstance(content, list) and len(content) > 0:
                import pandas as pd
                df = pd.DataFrame(content)

                # Mostrar contador de resultados
                st.caption(f"📊 {len(df)} resultado(s) encontrado(s)")

                # Renderizar com st.dataframe moderno
                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True
                )

                # Opção de download
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="⬇️ Download CSV",
                    data=csv,
                    file_name=f"dados_caculinha_{int(time.time())}.csv",
                    mime="text/csv",
                    key=f"download_{int(time.time() * 1000)}"
                )

        elif content_type == "chart":
            # Gráfico Plotly
            st.plotly_chart(content, use_container_width=True, key=f"chart_{int(time.time() * 1000)}")

        elif content_type == "text":
            # Texto simples (fallback)
            st.markdown(content)

        else:
            # Tipo desconhecido
            st.write(content)

    @staticmethod
    def show_thinking_indicator() -> None:
        """
        Mostra indicador animado de "pensando..."

        Use em um placeholder durante processamento
        """
        st.markdown(
            """
            <style>
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.5; }
            }
            .thinking-indicator {
                display: flex;
                align-items: center;
                gap: 8px;
                color: #8e8ea0;
                font-size: 14px;
                animation: pulse 2s ease-in-out infinite;
            }
            </style>
            <div class="thinking-indicator">
                🧠 Analisando sua pergunta...
            </div>
            """,
            unsafe_allow_html=True
        )

    @staticmethod
    def render_welcome_message() -> None:
        """Renderiza mensagem de boas-vindas conversacional"""
        st.markdown(
            """
            <div style="
                background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
                border-radius: 12px;
                padding: 24px;
                margin: 16px 0;
                text-align: center;
            ">
                <h2 style="margin:0; color: #ececf1;">👋 Oi! Sou a Caculinha</h2>
                <p style="margin: 12px 0 0 0; color: #8e8ea0; font-size: 16px;">
                    Sua assistente de dados conversacional. Pode me perguntar o que quiser sobre seus produtos,
                    estoques e vendas. Vou te ajudar! 😊
                </p>
                <div style="margin-top: 16px; font-size: 13px; color: #8e8ea0;">
                    💡 <b>Dica:</b> Você pode conversar naturalmente comigo.
                    Se eu não entender algo, vou te perguntar!
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    @staticmethod
    def render_error_message(error: str, suggestions: list = None) -> None:
        """
        Renderiza mensagem de erro de forma amigável

        Args:
            error: Mensagem de erro
            suggestions: Lista de sugestões para o usuário
        """
        st.error(f"😕 {error}")

        if suggestions:
            st.info("💡 **Sugestões:**\n" + "\n".join(f"- {s}" for s in suggestions))


def render_response_with_reasoning(
    response: Dict[str, Any],
    reasoning_result: Dict[str, Any] = None,
    show_debug: bool = False
) -> None:
    """
    Renderiza resposta com suporte a reasoning conversacional

    Args:
        response: Dicionário de resposta do backend
        reasoning_result: Resultado do reasoning (modo, tom emocional, etc.)
        show_debug: Se deve mostrar informações de debug
    """
    ui = ConversationalUI()

    # Extrair informações
    response_type = response.get("type", "text")
    content = response.get("content")
    reasoning_mode = reasoning_result.get("mode", "analytical") if reasoning_result else "analytical"
    emotional_tone = reasoning_result.get("emotional_tone", "neutro") if reasoning_result else "neutro"
    intent = response.get("intent", "resposta_simples")

    # Debug info (se habilitado)
    if show_debug and reasoning_result:
        with st.expander("🔍 Debug Info (Reasoning)"):
            st.json({
                "mode": reasoning_mode,
                "emotional_tone": emotional_tone,
                "confidence": reasoning_result.get("confidence", 0),
                "reasoning": reasoning_result.get("reasoning", "N/A"),
                "needs_clarification": reasoning_result.get("needs_clarification", False)
            })

    # Renderizar baseado no modo
    if reasoning_mode == "conversational" or response_type == "text":
        # Modo conversacional
        ui.render_conversational_message(
            content=str(content),
            emotional_tone=emotional_tone,
            show_streaming=True  # Streaming habilitado
        )

    elif response_type == "data":
        # Modo analítico - dados
        ui.render_analytical_message(
            content=content,
            content_type="data",
            intent=intent
        )

    elif response_type == "chart":
        # Modo analítico - gráfico
        ui.render_analytical_message(
            content=content,
            content_type="chart",
            intent=intent
        )

    else:
        # Fallback
        st.write(content)
