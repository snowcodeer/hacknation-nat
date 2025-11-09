<script lang="ts">
	import { aircraft, setComponentModel, setAllComponents } from '$lib/stores/aircraftStore';

	let chatInput = '';
	let isGenerating = false;
	let chatHistory: Array<{ role: 'user' | 'assistant'; message: string }> = [];

	const examples = [
		'Build me an F-22 Raptor fighter jet',
		'Create a Boeing 747 commercial airliner',
		'Design a small private Cessna plane',
		'Make a C-130 cargo aircraft'
	];

	async function handleSubmit() {
		if (!chatInput.trim() || isGenerating) return;

		const userMessage = chatInput.trim();
		chatInput = '';

		// Add user message to history
		chatHistory = [...chatHistory, { role: 'user', message: userMessage }];
		isGenerating = true;

		try {
			const response = await fetch('/api/generate/from-chat', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ prompt: userMessage })
			});

			const data = await response.json();

			if (data.success && data.aircraft_params) {
				// Add assistant message
				chatHistory = [
					...chatHistory,
					{
						role: 'assistant',
						message: `Generated ${userMessage}! Click "Apply to Aircraft" to see it.`
					}
				];

				// Apply parameters to all components
				applyAircraftParams(data.aircraft_params);
			} else {
				chatHistory = [
					...chatHistory,
					{
						role: 'assistant',
						message: `Error: ${data.error || 'Failed to generate aircraft'}`
					}
				];
			}
		} catch (error) {
			console.error('Chat error:', error);
			chatHistory = [
				...chatHistory,
				{ role: 'assistant', message: `Error: ${error instanceof Error ? error.message : 'Unknown error'}` }
			];
		} finally {
			isGenerating = false;
		}
	}

	function applyAircraftParams(params: any) {
		// Apply parameters to each component
		for (const [componentType, componentParams] of Object.entries(params)) {
			if (componentParams) {
				// Generate each component with these parameters
				generateComponent(componentType, componentParams as any);
			}
		}
	}

	async function generateComponent(componentType: string, parameters: any) {
		try {
			const response = await fetch('/api/generate/update-parameters', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ parameters })
			});

			const data = await response.json();

			if (data.success && data.model) {
				setComponentModel(componentType, data.model);
			}
		} catch (error) {
			console.error(`Error generating ${componentType}:`, error);
		}
	}

	function useExample(example: string) {
		chatInput = example;
	}
</script>

<div class="aircraft-chat">
	<h2>✈️ AI Aircraft Designer</h2>
	<p class="subtitle">Describe any aircraft in natural language</p>

	<div class="examples">
		<p class="examples-label">Try these:</p>
		{#each examples as example}
			<button class="example-btn" on:click={() => useExample(example)}>
				{example}
			</button>
		{/each}
	</div>

	<div class="chat-history">
		{#each chatHistory as message}
			<div class="message {message.role}">
				<div class="message-icon">{message.role === 'user' ? '👤' : '🤖'}</div>
				<div class="message-content">{message.message}</div>
			</div>
		{/each}
		{#if isGenerating}
			<div class="message assistant">
				<div class="message-icon">🤖</div>
				<div class="message-content">Generating aircraft parameters...</div>
			</div>
		{/if}
	</div>

	<form on:submit|preventDefault={handleSubmit} class="chat-input-form">
		<input
			type="text"
			bind:value={chatInput}
			placeholder="Describe your aircraft... (e.g., 'F-16 fighter jet')"
			disabled={isGenerating}
		/>
		<button type="submit" disabled={!chatInput.trim() || isGenerating}>
			{isGenerating ? 'Generating...' : 'Generate'}
		</button>
	</form>
</div>

<style>
	.aircraft-chat {
		background: var(--color-bg-secondary, #1e293b);
		border-radius: 8px;
		padding: 1.5rem;
		margin: 1rem 0;
	}

	h2 {
		margin: 0 0 0.5rem 0;
		color: var(--color-accent, #3b82f6);
	}

	.subtitle {
		margin: 0 0 1rem 0;
		color: var(--color-text-secondary, #94a3b8);
		font-size: 0.9rem;
	}

	.examples {
		margin-bottom: 1rem;
		padding: 1rem;
		background: var(--color-bg, #0f172a);
		border-radius: 6px;
	}

	.examples-label {
		margin: 0 0 0.5rem 0;
		font-size: 0.85rem;
		color: var(--color-text-secondary, #94a3b8);
	}

	.example-btn {
		display: inline-block;
		margin: 0.25rem;
		padding: 0.4rem 0.8rem;
		background: var(--color-bg-tertiary, #334155);
		border: 1px solid var(--color-border, #475569);
		border-radius: 4px;
		color: var(--color-text, #e2e8f0);
		font-size: 0.85rem;
		cursor: pointer;
		transition: all 0.2s;
	}

	.example-btn:hover {
		background: var(--color-accent, #3b82f6);
		border-color: var(--color-accent, #3b82f6);
	}

	.chat-history {
		max-height: 300px;
		overflow-y: auto;
		margin-bottom: 1rem;
		padding: 0.5rem;
		background: var(--color-bg, #0f172a);
		border-radius: 6px;
	}

	.message {
		display: flex;
		gap: 0.75rem;
		margin-bottom: 1rem;
		padding: 0.75rem;
		border-radius: 6px;
	}

	.message.user {
		background: var(--color-bg-tertiary, #334155);
	}

	.message.assistant {
		background: var(--color-accent-dark, #1e40af);
	}

	.message-icon {
		font-size: 1.5rem;
		flex-shrink: 0;
	}

	.message-content {
		flex: 1;
		color: var(--color-text, #e2e8f0);
		line-height: 1.5;
	}

	.chat-input-form {
		display: flex;
		gap: 0.5rem;
	}

	input {
		flex: 1;
		padding: 0.75rem;
		background: var(--color-bg, #0f172a);
		border: 1px solid var(--color-border, #475569);
		border-radius: 6px;
		color: var(--color-text, #e2e8f0);
		font-size: 0.95rem;
	}

	input:focus {
		outline: none;
		border-color: var(--color-accent, #3b82f6);
	}

	button[type='submit'] {
		padding: 0.75rem 1.5rem;
		background: var(--color-accent, #3b82f6);
		color: white;
		border: none;
		border-radius: 6px;
		font-weight: 500;
		cursor: pointer;
		transition: background 0.2s;
	}

	button[type='submit']:hover:not(:disabled) {
		background: var(--color-accent-dark, #2563eb);
	}

	button[type='submit']:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}
</style>
