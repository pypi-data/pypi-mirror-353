pub mod invalid_projection_variable;
pub mod uncompacted_uri;
pub mod undeclared_prefix;
pub mod ungrouped_select_variable;
pub mod unused_prefix_declaration;

use crate::server::{
    lsp::{
        diagnostic::Diagnostic, errors::LSPError, DiagnosticRequest, DiagnosticResponse,
        WorkspaceEditRequest,
    },
    message_handler::code_action::declare_prefix,
    Server,
};
use futures::lock::Mutex;
use ll_sparql_parser::{
    ast::{AstNode, QueryUnit},
    parse,
};
use std::{collections::HashMap, rc::Rc};

use super::code_action::remove_prefix_declaration;

pub(super) async fn handle_diagnostic_request(
    server_rc: Rc<Mutex<Server>>,
    request: DiagnosticRequest,
) -> Result<(), LSPError> {
    let mut server = server_rc.lock().await;
    let document = server
        .state
        .get_document(&request.params.text_document.uri)?;
    let ast = QueryUnit::cast(parse(&document.text)).ok_or(LSPError::new(
        crate::server::lsp::errors::ErrorCode::InternalError,
        "diagnostics are currently only supported for query operations",
    ))?;
    let mut diagnostic_accu = Vec::new();
    macro_rules! add {
        ($diagnostic_provider:path) => {
            if let Some(diagnostics) = $diagnostic_provider(document, &ast, &server) {
                diagnostic_accu.extend(diagnostics);
            }
        };
    }
    add!(unused_prefix_declaration::diagnostics);
    add!(undeclared_prefix::diagnostics);
    add!(uncompacted_uri::diagnostics);
    add!(uncompacted_uri::diagnostics);
    add!(ungrouped_select_variable::diagnostics);
    add!(invalid_projection_variable::diagnostics);

    if client_support_workspace_edits(&server) && server.settings.manage_prefix_declarations {
        declare_and_undeclare_prefixes(&mut server, &request, &diagnostic_accu);
    }

    server.send_message(DiagnosticResponse::new(request.get_id(), diagnostic_accu))
}

fn declare_and_undeclare_prefixes(
    server: &mut Server,
    request: &DiagnosticRequest,
    diagnostics: &Vec<Diagnostic>,
) {
    let document_uri = request.params.text_document.uri.clone();
    let edits: Vec<_> = diagnostics
        .iter()
        .filter_map(|diagnostic| {
            match diagnostic.code.as_ref() {
                Some(code) if code == &*undeclared_prefix::CODE => {
                    declare_prefix(&server, &document_uri, diagnostic.clone())
                }
                Some(code) if code == &*unused_prefix_declaration::CODE => {
                    remove_prefix_declaration(server, &document_uri, diagnostic.clone())
                }
                _ => Ok(None),
            }
            .ok()
            .flatten()
            .and_then(|code_action| code_action.edit.changes)
            .and_then(|mut changes| changes.remove(&document_uri))
        })
        .flatten()
        .collect();
    if !edits.is_empty() {
        let request_id = server.bumb_request_id();
        if let Err(err) = server.send_message(WorkspaceEditRequest::new(
            request_id,
            HashMap::from_iter([(document_uri, edits)]),
        )) {
            log::error!("Sending \"workspace/applyEdit\" request failed:\n{:?}", err);
        }
    }
}

fn client_support_workspace_edits(server: &Server) -> bool {
    server
        .client_capabilities
        .as_ref()
        .is_some_and(|client_capabilities| {
            client_capabilities
                .workspace
                .as_ref()
                .and_then(|workspace_capablities| workspace_capablities.apply_edit)
                .is_some_and(|flag| flag)
                && client_capabilities
                    .workspace
                    .as_ref()
                    .and_then(|workspace_capablities| workspace_capablities.workspace_edit.as_ref())
                    .is_some_and(|capability| capability.document_changes.is_some_and(|flag| flag))
        })
}
