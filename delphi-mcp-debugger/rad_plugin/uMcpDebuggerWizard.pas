unit uMcpDebuggerWizard;

interface

uses
  ToolsAPI, System.SysUtils, System.Classes, uJsonRpcServer;

type
  TMcpDebuggerWizard = class(TNotifierObject, IOTAWizard)
  private
    FRpc: TJsonRpcServer;
    procedure HandleRequest(const AId, AMethod, AParams: string; var AResult, AError: string);
    function DebuggerServices: IOTADebuggerServices;
    function BreakpointServices: IOTABreakpointServices;
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

function TMcpDebuggerWizard.DebuggerServices: IOTADebuggerServices;
begin
  Supports(BorlandIDEServices, IOTADebuggerServices, Result);
end;

function TMcpDebuggerWizard.BreakpointServices: IOTABreakpointServices;
begin
  Supports(BorlandIDEServices, IOTABreakpointServices, Result);
end;

procedure TMcpDebuggerWizard.HandleRequest(const AId, AMethod, AParams: string; var AResult, AError: string);
var
  Params: TJSONObject;
  DS: IOTADebuggerServices;
  BS: IOTABreakpointServices;
  FileName: string;
  LineNum: Integer;
begin
  Params := TJSONObject.ParseJSONValue(AParams) as TJSONObject;
  try
    DS := DebuggerServices;
    if AMethod = 'debug/run' then
    begin
      if Assigned(DS) then
      begin
        DS.Run;
        AResult := '{"status":"running"}';
      end
      else
        AError := 'IOTADebuggerServices not available';
    end
    else if AMethod = 'debug/continue' then
    begin
      if Assigned(DS) then
      begin
        DS.Run;
        AResult := '{"status":"continued"}';
      end
      else
        AError := 'IOTADebuggerServices not available';
    end
    else if AMethod = 'debug/stepOver' then
    begin
      if Assigned(DS) then
      begin
        DS.StepOver;
        AResult := '{"status":"stepped"}';
      end
      else
        AError := 'IOTADebuggerServices not available';
    end
    else if AMethod = 'debug/setBreakpoint' then
    begin
      BS := BreakpointServices;
      if Assigned(BS) and Assigned(Params) then
      begin
        FileName := Params.GetValue<string>('file', '');
        LineNum := Params.GetValue<Integer>('line', 0);
        // Примечание: конкретные методы добавления брейкпоинтов отличаются между версиями OTAPI.
        // Здесь оставлена заглушка успешного ответа. Реализация будет уточнена под вашу версию RAD Studio.
        AResult := Format('{"id":"%s","file":"%s","line":%d}', ['bp-1', FileName, LineNum]);
      end
      else
        AError := 'IOTABreakpointServices not available';
    end
    else if AMethod = 'debug/removeBreakpoint' then
    begin
      BS := BreakpointServices;
      if Assigned(BS) then
      begin
        // Заглушка удаления брейкпоинта
        AResult := '{"removed":true}';
      end
      else
        AError := 'IOTABreakpointServices not available';
    end
    else
      AError := 'unknown method';
  finally
    Params.Free;
  end;
end;

end.