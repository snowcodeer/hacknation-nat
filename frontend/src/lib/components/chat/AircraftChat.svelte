<script lang="ts">
	import { aircraft, setComponentModel } from '$lib/stores/aircraftStore';
	import { apiService } from '$lib/services/apiService';

	let chatInput = '';
	let isGenerating = false;
	let chatHistory: Array<{ role: 'user' | 'assistant'; message: string; timestamp: string }> = [];
	let hasStartedChat = false;

	const examples = [
		'Build me an F-22 Raptor fighter jet',
		'Create a Boeing 747 commercial airliner',
		'Design a small private Cessna plane',
		'Make a C-130 cargo aircraft'
	];

	function formatTimestamp(): string {
		const now = new Date();
		return `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`;
	}

	async function handleSubmit() {
		if (!chatInput.trim() || isGenerating) return;

		const userMessage = chatInput.trim();
		chatInput = '';

		// Add user message to history
		chatHistory = [...chatHistory, { role: 'user', message: userMessage, timestamp: formatTimestamp() }];
		hasStartedChat = true;
		isGenerating = true;

		try {
			// Check if any components exist (for edit mode)
			const hasExistingComponents = $aircraft.wings.model || $aircraft.fuselage.model || $aircraft.engines.model;

			// Keywords that suggest editing vs generation
			const editKeywords = ['make', 'set', 'change', 'increase', 'decrease', 'rotate', 'move', 'bigger', 'smaller', 'adjust', 'modify'];
			const lowerMessage = userMessage.toLowerCase();
			const seemsLikeEdit = editKeywords.some(keyword => lowerMessage.includes(keyword));

			// Try edit mode if components exist and prompt seems like an edit
			if (hasExistingComponents && seemsLikeEdit) {
				try {
					const editResult = await apiService.editComponent(userMessage, $aircraft);

					if (editResult.success && editResult.model) {
						// Update the edited component
						const componentType = editResult.component as 'wings' | 'fuselage' | 'engines';
						setComponentModel(componentType, editResult.model);

						// Add success message
						chatHistory = [
							...chatHistory,
							{
								role: 'assistant',
								message: `✓ ${editResult.description || `Updated ${componentType}`}. Check the 3D preview to see the changes!`,
								timestamp: formatTimestamp()
							}
						];
						isGenerating = false;
						return;
					} else if (editResult.error && editResult.error.includes('not yet implemented')) {
						// If operation not implemented, show friendly message
						chatHistory = [
							...chatHistory,
							{
								role: 'assistant',
								message: `Note: ${editResult.error}`,
								timestamp: formatTimestamp()
							}
						];
						isGenerating = false;
						return;
					}
					// If edit failed, fall through to generation mode
				} catch (editError) {
					console.log('Edit attempt failed, trying generation mode:', editError);
					// Fall through to generation mode
				}
			}

			// Generation mode (new aircraft or edit failed)
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
						message: `Generated ${userMessage} and applied to aircraft! Check the 3D preview and component tabs.`,
						timestamp: formatTimestamp()
					}
				];

				// Apply parameters to all components
				applyAircraftParams(data.aircraft_params);
			} else {
				chatHistory = [
					...chatHistory,
					{
						role: 'assistant',
						message: `Error: ${data.error || 'Failed to generate aircraft'}`,
						timestamp: formatTimestamp()
					}
				];
			}
		} catch (error) {
			console.error('Chat error:', error);
			chatHistory = [
				...chatHistory,
				{
					role: 'assistant',
					message: `Error: ${error instanceof Error ? error.message : 'Unknown error'}`,
					timestamp: formatTimestamp()
				}
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

	// Convert backend snake_case to frontend camelCase
	function convertBackendModel(backendModel: any): any {
		return {
			...backendModel,
			parameters: {
				wingType: backendModel.parameters.wing_type,
				span: backendModel.parameters.span,
				rootChord: backendModel.parameters.root_chord,
				tipChord: backendModel.parameters.tip_chord,
				sweepAngle: backendModel.parameters.sweep_angle,
				thickness: backendModel.parameters.thickness,
				dihedral: backendModel.parameters.dihedral,
				fuselageType: backendModel.parameters.fuselage_type,
				fuselageLength: backendModel.parameters.fuselage_length,
				fuselageDiameter: backendModel.parameters.fuselage_diameter,
				engineLength: backendModel.parameters.engine_length,
				engineDiameter: backendModel.parameters.engine_diameter,
				hasVerticalStabilizer: backendModel.parameters.has_vertical_stabilizer,
				hasHorizontalStabilizer: backendModel.parameters.has_horizontal_stabilizer,
				positionX: backendModel.parameters.position_x,
				positionY: backendModel.parameters.position_y,
				positionZ: backendModel.parameters.position_z
			}
		};
	}

	async function generateComponent(componentType: string, parameters: any) {
		try {
			// Parameters from chat endpoint are already in snake_case, send directly
			const response = await fetch('/api/generate/update-parameters', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ parameters })
			});

			const data = await response.json();

			if (data.success && data.model) {
				// Convert backend model to frontend format before storing
				const frontendModel = convertBackendModel(data.model);
				setComponentModel(componentType, frontendModel);
			}
		} catch (error) {
			console.error(`Error generating ${componentType}:`, error);
		}
	}

	function useExample(example: string) {
		chatInput = example;
	}
</script>

<div class="copilot-container">
	<!-- Header -->
	<div class="copilot-header">
		<div class="header-row">
			<h2 class="copilot-title">AI Co-Pilot</h2>
			<div class="status-indicator active">
				<div class="indicator-pulse"></div>
				<span>ONLINE</span>
			</div>
		</div>
	</div>

	<!-- Chat Log -->
	<div class="chat-log">
		<!-- Quick Commands (shown before first message) -->
		{#if !hasStartedChat}
			<div class="quick-commands">
				<div class="commands-header">
					<svg viewBox="0 0 16 16" fill="none">
						<path d="M2 8L8 2L14 8M8 3V14" stroke="currentColor" stroke-width="1.5"/>
					</svg>
					<span>QUICK COMMANDS</span>
				</div>
				<div class="commands-grid">
					{#each examples as example}
						<button class="command-btn" on:click={() => useExample(example)} disabled={isGenerating}>
							<svg viewBox="0 0 16 16" fill="none" class="command-icon">
								<path d="M4 8H12M12 8L9 5M12 8L9 11" stroke="currentColor" stroke-width="1.5"/>
							</svg>
							<span>{example}</span>
						</button>
					{/each}
				</div>
			</div>
		{/if}

		<!-- Messages -->
		{#if chatHistory.length > 0}
			{#each chatHistory as message}
				<div class="message {message.role}">
					<div class="message-header">
						<div class="message-sender">
							{#if message.role === 'user'}
								<svg viewBox="0 0 16 16" fill="none">
									<circle cx="8" cy="5" r="3" stroke="currentColor" stroke-width="1.5"/>
									<path d="M2 14C2 11 5 9 8 9C11 9 14 11 14 14" stroke="currentColor" stroke-width="1.5"/>
								</svg>
								<span>USER</span>
							{:else}
								<svg viewBox="0 0 16 16" fill="none">
									<rect x="3" y="3" width="10" height="10" rx="2" stroke="currentColor" stroke-width="1.5"/>
									<circle cx="6" cy="7" r="0.5" fill="currentColor"/>
									<circle cx="10" cy="7" r="0.5" fill="currentColor"/>
									<path d="M6 10L8 11L10 10" stroke="currentColor" stroke-width="1.5"/>
								</svg>
								<span>AI-COPILOT</span>
							{/if}
						</div>
						<span class="message-time">{message.timestamp}</span>
					</div>
					<div class="message-content">{message.message}</div>
				</div>
			{/each}
		{/if}

		{#if isGenerating}
			<div class="message assistant generating">
				<div class="message-header">
					<div class="message-sender">
						<svg viewBox="0 0 16 16" fill="none">
							<rect x="3" y="3" width="10" height="10" rx="2" stroke="currentColor" stroke-width="1.5"/>
							<circle cx="6" cy="7" r="0.5" fill="currentColor"/>
							<circle cx="10" cy="7" r="0.5" fill="currentColor"/>
							<path d="M6 10L8 11L10 10" stroke="currentColor" stroke-width="1.5"/>
						</svg>
						<span>AI-COPILOT</span>
					</div>
					<span class="message-time">{formatTimestamp()}</span>
				</div>
				<div class="message-content">
					<div class="processing">
						<div class="processing-dots">
							<div class="dot"></div>
							<div class="dot"></div>
							<div class="dot"></div>
						</div>
						<span>Processing aircraft parameters...</span>
					</div>
				</div>
			</div>
		{/if}
	</div>

	<!-- Input Area -->
	<form on:submit|preventDefault={handleSubmit} class="input-area">
		<div class="input-wrapper">
			<svg viewBox="0 0 16 16" fill="none" class="input-icon">
				<path d="M2 8H14M8 2V14" stroke="currentColor" stroke-width="1.5"/>
			</svg>
			<input
				type="text"
				bind:value={chatInput}
				placeholder="Describe aircraft specification..."
				disabled={isGenerating}
				class="input-field"
			/>
		</div>
		<button type="submit" disabled={!chatInput.trim() || isGenerating} class="send-btn">
			{#if isGenerating}
				<div class="spinner-btn"></div>
			{:else}
				<svg viewBox="0 0 16 16" fill="none">
					<path d="M2 8L14 2L10 8L14 14L2 8Z" fill="currentColor"/>
				</svg>
			{/if}
		</button>
	</form>
</div>

<style>
	.copilot-container {
		height: 100%;
		display: flex;
		flex-direction: column;
		background: var(--blueprint-bg-secondary);
	}

	/* HEADER */
	.copilot-header {
		padding: var(--space-3) var(--space-4);
		border-bottom: 1px solid var(--border-technical);
		background: var(--blueprint-surface);
		flex-shrink: 0;
	}

	.header-row {
		display: flex;
		justify-content: space-between;
		align-items: center;
	}

	.copilot-title {
		font-size: 0.875rem;
		font-weight: 700;
		color: var(--gray-100);
		margin: 0;
		letter-spacing: 0.05em;
		text-transform: uppercase;
	}

	.status-indicator {
		display: flex;
		align-items: center;
		gap: var(--space-2);
		font-size: 0.5625rem;
		font-weight: 700;
		letter-spacing: 0.1em;
		color: var(--gray-400);
	}

	.status-indicator.active {
		color: var(--green-success);
	}

	.indicator-pulse {
		width: 6px;
		height: 6px;
		border-radius: 50%;
		background: var(--green-success);
		box-shadow: 0 0 8px var(--green-glow);
		animation: pulse-bright 2s infinite;
	}

	@keyframes pulse-bright {
		0%, 100% {
			opacity: 1;
			transform: scale(1);
		}
		50% {
			opacity: 0.7;
			transform: scale(0.85);
		}
	}

	/* QUICK COMMANDS */
	.quick-commands {
		padding: var(--space-4);
	}

	.commands-header {
		display: flex;
		align-items: center;
		gap: var(--space-2);
		margin-bottom: var(--space-3);
		font-size: 0.5625rem;
		font-weight: 700;
		letter-spacing: 0.1em;
		color: var(--gray-500);
	}

	.commands-header svg {
		width: 12px;
		height: 12px;
	}

	.commands-grid {
		display: flex;
		flex-direction: column;
		gap: var(--space-2);
	}

	.command-btn {
		display: flex;
		align-items: center;
		gap: var(--space-2);
		padding: var(--space-2) var(--space-3);
		background: var(--blueprint-surface);
		border: 1px solid var(--border-subtle);
		color: var(--gray-300);
		font-size: 0.6875rem;
		text-align: left;
		cursor: pointer;
		transition: all 0.2s;
		line-height: 1.3;
	}

	.command-icon {
		width: 12px;
		height: 12px;
		flex-shrink: 0;
		color: var(--cyan-500);
	}

	.command-btn:hover:not(:disabled) {
		background: var(--blueprint-bg);
		border-color: var(--cyan-600);
		color: var(--gray-100);
		transform: translateX(2px);
	}

	.command-btn:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	/* CHAT LOG */
	.chat-log {
		flex: 1;
		overflow-y: auto;
		display: flex;
		flex-direction: column;
		gap: var(--space-4);
		min-height: 0;
	}

	.chat-log > .quick-commands:first-child,
	.chat-log > .message:first-child {
		margin-top: var(--space-4);
	}

	.chat-log > .message:last-child,
	.chat-log > .message.generating:last-child {
		margin-bottom: var(--space-4);
	}

	.chat-log > .message {
		margin-left: var(--space-4);
		margin-right: var(--space-4);
	}

	/* MESSAGES */
	.message {
		display: flex;
		flex-direction: column;
		gap: var(--space-2);
		padding: var(--space-3);
		background: var(--blueprint-surface);
		border: 1px solid var(--border-subtle);
		border-left: 3px solid var(--border-subtle);
	}

	.message.user {
		border-left-color: var(--cyan-500);
		background: rgba(3, 169, 244, 0.05);
	}

	.message.assistant {
		border-left-color: var(--green-success);
		background: rgba(102, 187, 106, 0.05);
	}

	.message.generating {
		border-left-color: var(--amber-warning);
		background: rgba(255, 167, 38, 0.05);
		animation: pulse-message 2s infinite;
	}

	@keyframes pulse-message {
		0%, 100% {
			opacity: 1;
		}
		50% {
			opacity: 0.8;
		}
	}

	.message-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: var(--space-1);
	}

	.message-sender {
		display: flex;
		align-items: center;
		gap: var(--space-2);
		font-size: 0.5625rem;
		font-weight: 700;
		letter-spacing: 0.1em;
		color: var(--gray-400);
	}

	.message.user .message-sender {
		color: var(--cyan-400);
	}

	.message.assistant .message-sender {
		color: var(--green-success);
	}

	.message.generating .message-sender {
		color: var(--amber-warning);
	}

	.message-sender svg {
		width: 14px;
		height: 14px;
	}

	.message-time {
		font-family: var(--font-technical);
		font-size: 0.5625rem;
		color: var(--gray-500);
	}

	.message-content {
		font-size: 0.8125rem;
		line-height: 1.5;
		color: var(--gray-200);
	}

	.processing {
		display: flex;
		align-items: center;
		gap: var(--space-3);
	}

	.processing-dots {
		display: flex;
		gap: var(--space-1);
	}

	.dot {
		width: 4px;
		height: 4px;
		border-radius: 50%;
		background: var(--amber-warning);
		animation: bounce 1.4s infinite ease-in-out both;
	}

	.dot:nth-child(1) {
		animation-delay: -0.32s;
	}

	.dot:nth-child(2) {
		animation-delay: -0.16s;
	}

	@keyframes bounce {
		0%, 80%, 100% {
			transform: scale(0);
		}
		40% {
			transform: scale(1);
		}
	}

	/* INPUT AREA */
	.input-area {
		padding: var(--space-4);
		border-top: 1px solid var(--border-technical);
		background: var(--blueprint-surface);
		display: flex;
		gap: var(--space-2);
		flex-shrink: 0;
	}

	.input-wrapper {
		flex: 1;
		display: flex;
		align-items: center;
		gap: var(--space-2);
		padding: var(--space-3);
		background: var(--blueprint-bg);
		border: 1px solid var(--border-subtle);
		transition: all 0.2s;
	}

	.input-wrapper:focus-within {
		border-color: var(--cyan-500);
		box-shadow: 0 0 10px var(--cyan-glow);
	}

	.input-icon {
		width: 14px;
		height: 14px;
		color: var(--gray-500);
	}

	.input-field {
		flex: 1;
		background: transparent;
		border: none;
		outline: none;
		color: var(--gray-100);
		font-size: 0.8125rem;
		padding: 0;
	}

	.input-field::placeholder {
		color: var(--gray-500);
	}

	.send-btn {
		width: 44px;
		height: 44px;
		display: flex;
		align-items: center;
		justify-content: center;
		background: linear-gradient(135deg, var(--cyan-700), var(--cyan-600));
		border: 1px solid var(--cyan-500);
		color: white;
		cursor: pointer;
		transition: all 0.2s;
	}

	.send-btn svg {
		width: 16px;
		height: 16px;
	}

	.send-btn:hover:not(:disabled) {
		background: linear-gradient(135deg, var(--cyan-600), var(--cyan-500));
		box-shadow: 0 0 15px var(--cyan-glow);
		transform: translateY(-1px);
	}

	.send-btn:disabled {
		background: var(--blueprint-bg);
		border-color: var(--border-subtle);
		color: var(--gray-500);
		cursor: not-allowed;
	}

	.spinner-btn {
		width: 16px;
		height: 16px;
		border: 2px solid rgba(255, 255, 255, 0.3);
		border-top-color: white;
		border-radius: 50%;
		animation: spin 0.8s linear infinite;
	}

	@keyframes spin {
		to { transform: rotate(360deg); }
	}
</style>
