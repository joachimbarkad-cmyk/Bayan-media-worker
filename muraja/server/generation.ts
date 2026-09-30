/**
 * Interchangeable content-generation providers.
 *
 * The developer agents' accounts (Claude Code, Codex) are NEVER used here. With no provider
 * configured (the default, zero cost), every generation request returns an honest
 * "unavailable" answer and the app keeps working with manual editing and imports.
 */
export interface GenerationStatus { available: boolean; provider: string; message: string }

export interface GenerationProvider {
  name: string;
  status(): GenerationStatus;
  explainSimply(input: { text: string; glossary: string[] }): Promise<string>;
}

class NoProvider implements GenerationProvider {
  name = 'aucun';
  status(): GenerationStatus {
    return {
      available: false,
      provider: this.name,
      message: "La génération automatique n'est pas activée sur ce site. Vous pouvez écrire l'explication vous-même, " +
        "ou la préparer dans NotebookLM (ou un autre outil) à partir de votre cours, puis l'importer.",
    };
  }
  async explainSimply(): Promise<string> {
    throw new Error(this.status().message);
  }
}

export function loadProvider(env: NodeJS.ProcessEnv): GenerationProvider {
  // Only "none" exists for now. A future provider must be explicitly enabled by the owner,
  // with its own key and budget, and must store results instead of regenerating on each view.
  const wanted = env.MURAJA_GENERATION_PROVIDER ?? 'none';
  if (wanted !== 'none') {
    console.warn(`Fournisseur de génération inconnu "${wanted}" : génération désactivée.`);
  }
  return new NoProvider();
}
