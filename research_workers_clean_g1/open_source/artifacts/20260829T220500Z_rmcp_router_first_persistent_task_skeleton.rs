//! SOURCE-QUALIFIED SKELETON ONLY — NOT COMPILED IN THIS RUN.
//! Target: modelcontextprotocol/rust-sdk rmcp-v3.1.4 @
//! 4a738b9dd99eaca418b614afa433a0cbdaf8d056.
//!
//! Purpose: demonstrate the smallest router-first seam. The SDK macro-generated
//! `call_tool` remains in control, so `ToolRouter::call` performs disabled-route
//! checks and standard extractors before this handler body can materialize a task.
//! The durable store/executor below is deliberately an application abstraction;
//! stock `TaskManager` is NOT used because its storage is process-local.
//!
//! Cargo note: RequestStateCodec requires rmcp's `request-state` feature.

use std::{sync::Arc, time::Duration};

use rmcp::{
    ErrorData as McpError, ServerHandler, schemars, tool, tool_handler, tool_router,
    handler::server::{
        common::Extension,
        router::tool::ToolRouter,
        tool::RequestState,
        wrapper::Parameters,
    },
    model::{
        CallToolResponse, CancelTaskParams, ClientCapabilities, CreateTaskResult,
        DetailedTask, GetTaskParams, GetTaskResult, InputRequiredResult, RequestStateCodec,
        SealOptions, ServerCapabilities, ServerInfo, Task, UpdateTaskParams,
    },
    service::{RequestContext, RoleServer},
};
use serde::{Deserialize, Serialize};

#[derive(Clone, Debug)]
pub struct Principal(pub String);

#[derive(Debug, Clone, Serialize, Deserialize, schemars::JsonSchema)]
pub struct MutateArgs {
    pub value: i64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct PreflightState {
    op_id: String,
}

/// Application-owned persistent task store/executor.
///
/// REQUIRED contract (not supplied by rmcp):
/// - mint_op_id() returns a server-generated stable logical operation id.
/// - create_or_get is atomic on op_id and rejects intent-key conflicts.
/// - only the returned `created=true` winner may claim/schedule the operation.
/// - get/update/cancel survive server-process restart.
/// - restart redrive uses an attempt generation/CAS; external effects use their
///   own stable idempotency key or fencing.
pub trait DurableTaskStore: Send + Sync + 'static {
    fn mint_op_id(&self) -> Result<String, McpError>;
    fn create_or_get(
        &self,
        op_id: &str,
        intent_key: &str,
    ) -> Result<(Task, bool), McpError>;
    fn schedule_if_winner(&self, task_id: &str, args: MutateArgs) -> Result<(), McpError>;
    fn get(&self, task_id: &str) -> Result<DetailedTask, McpError>;
    fn update(
        &self,
        task_id: &str,
        input_responses: rmcp::model::InputResponses,
    ) -> Result<(), McpError>;
    fn cancel(&self, task_id: &str) -> Result<(), McpError>;
}

#[derive(Clone)]
pub struct TaskServer {
    tool_router: ToolRouter<Self>,
    store: Arc<dyn DurableTaskStore>,
    request_state: RequestStateCodec,
}

impl TaskServer {
    pub fn new(
        store: Arc<dyn DurableTaskStore>,
        signing_key: impl Into<Vec<u8>>,
    ) -> Result<Self, McpError> {
        let request_state = RequestStateCodec::try_new(signing_key)
            .map_err(|e| McpError::invalid_params(e.to_string(), None))?;
        Ok(Self {
            tool_router: Self::tool_router(),
            store,
            request_state,
        })
    }

    fn associated_data(principal: &Principal, args: &MutateArgs) -> Result<Vec<u8>, McpError> {
        // Production code should use a canonical representation and include any
        // authorization-relevant resource identity. The exact bytes must be
        // re-derived identically on the retry round.
        let args_json = serde_json::to_string(args)
            .map_err(|e| McpError::internal_error(e.to_string(), None))?;
        Ok(format!("{}|tools/call|mutate|{}", principal.0, args_json).into_bytes())
    }

    fn intent_key(principal: &Principal, args: &MutateArgs) -> Result<String, McpError> {
        // Exact canonical intent comparison is sufficient for create-or-get;
        // a production store may hash these bytes as an internal optimization.
        let bytes = Self::associated_data(principal, args)?;
        String::from_utf8(bytes).map_err(|e| McpError::internal_error(e.to_string(), None))
    }
}

#[tool_router]
impl TaskServer {
    #[tool(description = "Example persistent task-capable mutation")]
    async fn mutate(
        &self,
        Parameters(args): Parameters<MutateArgs>,
        context: RequestContext<RoleServer>,
        RequestState(request_state): RequestState,
        Extension(principal): Extension<Principal>,
    ) -> Result<CallToolResponse, McpError> {
        // IMPORTANT: this check is inside the registered handler, before
        // create_or_get. The generic Service dispatcher checks task capability
        // only after call_tool returns, which is too late to be a materialization fence.
        let client_supports_tasks = context
            .client_capabilities()
            .is_some_and(|caps| caps.supports_tasks());
        if !client_supports_tasks {
            return Err(McpError::missing_required_client_capability(
                ClientCapabilities::builder().enable_tasks().build(),
            ));
        }

        let associated_data = Self::associated_data(&principal, &args)?;

        let Some(sealed) = request_state else {
            // Round 1 is side-effect-free: no durable task row and no business effect.
            let op_id = self.store.mint_op_id()?;
            let sealed = self
                .request_state
                .seal_json_with(
                    &PreflightState { op_id },
                    &SealOptions::new()
                        .associated_data(&associated_data)
                        .ttl(Duration::from_secs(300)),
                )
                .map_err(|e| McpError::internal_error(e.to_string(), None))?;
            return Ok(InputRequiredResult::from_request_state(sealed).into());
        };

        // Round 2: ToolRouter + Parameters + Extension extractors have run again,
        // so current route policy and typed input validation precede materialization.
        let preflight: PreflightState = self
            .request_state
            .open_json_with(&sealed, &associated_data)
            .map_err(|e| McpError::invalid_params(e.to_string(), None))?;
        let intent_key = Self::intent_key(&principal, &args)?;
        let (task, created) = self.store.create_or_get(&preflight.op_id, &intent_key)?;
        if created {
            self.store.schedule_if_winner(&task.task_id, args)?;
        }
        Ok(CreateTaskResult::new(task).into())
    }
}

// No manual call_tool: #[tool_handler] generates the router-first implementation.
#[tool_handler]
impl ServerHandler for TaskServer {
    fn get_info(&self) -> ServerInfo {
        ServerInfo::new(
            ServerCapabilities::builder()
                .enable_tools()
                .enable_tasks()
                .build(),
        )
    }

    async fn get_task(
        &self,
        request: GetTaskParams,
        _context: RequestContext<RoleServer>,
    ) -> Result<GetTaskResult, McpError> {
        Ok(GetTaskResult::new(self.store.get(&request.task_id)?))
    }

    async fn update_task(
        &self,
        request: UpdateTaskParams,
        _context: RequestContext<RoleServer>,
    ) -> Result<(), McpError> {
        self.store.update(&request.task_id, request.input_responses)
    }

    async fn cancel_task(
        &self,
        request: CancelTaskParams,
        _context: RequestContext<RoleServer>,
    ) -> Result<(), McpError> {
        self.store.cancel(&request.task_id)
    }
}

// Source-check notes for the next run:
// 1. Verify this exact file with real rustc/cargo; neither exists in the current runtime.
// 2. Verify how the authenticated Principal is inserted into RequestContext.extensions
//    for the selected transport/middleware; Extension<Principal> itself is an exact rmcp extractor.
// 3. Verify the application store returns the exact same seed Task on duplicate op_id and
//    persists any in-task inputRequests needed by tasks/update.
// 4. DurableTaskStore must not schedule an effect before its row/intent is committed,
//    and must independently solve create-before-schedule crash redrive and effect fencing.
