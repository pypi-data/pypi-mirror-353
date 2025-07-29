import {
  CompletionHandler,
  IInlineCompletionContext
} from '@jupyterlab/completer';
import { AIMessage, SystemMessage } from '@langchain/core/messages';
import { ChatOllama } from '@langchain/ollama';

import { BaseCompleter, IBaseCompleter } from '../../base-completer';
import { COMPLETION_SYSTEM_PROMPT } from '../../provider';

export class OllamaCompleter implements IBaseCompleter {
  constructor(options: BaseCompleter.IOptions) {
    this._completer = new ChatOllama({ ...options.settings });
  }

  /**
   * Getter and setter for the initial prompt.
   */
  get prompt(): string {
    return this._prompt;
  }
  set prompt(value: string) {
    this._prompt = value;
  }

  async fetch(
    request: CompletionHandler.IRequest,
    context: IInlineCompletionContext
  ) {
    const { text, offset: cursorOffset } = request;
    const prompt = text.slice(0, cursorOffset);

    const messages = [new SystemMessage(this._prompt), new AIMessage(prompt)];

    try {
      const response = await this._completer.invoke(messages);
      const items = [];
      if (typeof response.content === 'string') {
        items.push({
          insertText: response.content
        });
      } else {
        response.content.forEach(content => {
          if (content.type !== 'text') {
            return;
          }
          items.push({
            insertText: content.text,
            filterText: prompt.substring(prompt.length)
          });
        });
      }
      return { items };
    } catch (error) {
      console.error('Error fetching completions', error);
      return { items: [] };
    }
  }

  private _completer: ChatOllama;
  private _prompt: string = COMPLETION_SYSTEM_PROMPT;
}
