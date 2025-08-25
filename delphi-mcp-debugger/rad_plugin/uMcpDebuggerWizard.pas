unit uMcpDebuggerWizard;

interface

uses
  ToolsAPI, System.SysUtils, System.Classes, uJsonRpcServer;

type
  TMcpDebuggerWizard = class(TNotifierObject, IOTAWizard)
  private
    FRpc: TJsonRpcServer;
    procedure HandleRequest(const AId, AMethod, AParams: string; var AResult, AError: string);
  public
    constructor Create;
    destructor Destroy; override;
    // IOTAWizard
    function GetIDString: string;
    function GetName: string;
    function GetState: TWizardState;
    procedure Execute;
  end;

procedure Register;

implementation

uses
  System.JSON;

procedure Register;
begin
  RegisterPackageWizard(TMcpDebuggerWizard.Create);
end;

{ TMcpDebuggerWizard }

constructor TMcpDebuggerWizard.Create;
var
  LPort: Integer;
  LToken: string;
begin
  inherited Create;
  FRpc := TJsonRpcServer.Create(nil);
  FRpc.OnRequest := HandleRequest;
  LPort := StrToIntDef(GetEnvironmentVariable('RAD_PLUGIN_PORT'), 5645);
  LToken := GetEnvironmentVariable('RAD_PLUGIN_TOKEN');
  FRpc.Start('127.0.0.1', LPort, LToken);
end;

destructor TMcpDebuggerWizard.Destroy;
begin
  FRpc.Stop;
  FRpc.Free;
  inherited;
end;

procedure TMcpDebuggerWizard.Execute;
begin
  // no UI
end;

function TMcpDebuggerWizard.GetIDString: string;
begin
  Result := 'Delphi.MCP.Debugger.Wizard';
end;

function TMcpDebuggerWizard.GetName: string;
begin
  Result := 'Delphi MCP Debugger';
end;

function TMcpDebuggerWizard.GetState: TWizardState;
begin
  Result := [wsEnabled];
end;

procedure TMcpDebuggerWizard.HandleRequest(const AId, AMethod, AParams: string; var AResult, AError: string);
var
  Params: TJSONObject;
begin
  Params := TJSONObject.ParseJSONValue(AParams) as TJSONObject;
  try
    if AMethod = 'debug/run' then
    begin
      // TODO: IOTADebuggerServices.Run
      AResult := '{"status":"running"}';
    end
    else if AMethod = 'debug/continue' then
    begin
      // TODO: IOTADebuggerServices.Run or Continue
      AResult := '{"status":"continued"}';
    end
    else if AMethod = 'debug/stepOver' then
    begin
      // TODO: IOTADebuggerServices.StepOver
      AResult := '{"status":"stepped"}';
    end
    else if AMethod = 'debug/setBreakpoint' then
    begin
      // TODO: IOTABreakpointServices.AddBreakpoint
      AResult := '{"id":"bp-1"}';
    end
    else if AMethod = 'debug/removeBreakpoint' then
    begin
      // TODO: IOTABreakpointServices to remove
      AResult := '{"removed":true}';
    end
    else
      AError := 'unknown method';
  finally
    Params.Free;
  end;
end;

end.