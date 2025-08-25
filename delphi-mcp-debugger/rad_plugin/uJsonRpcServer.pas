unit uJsonRpcServer;

interface

uses
  System.SysUtils, System.Classes,
  IdContext, IdCustomTCPServer, IdTCPServer;

type
  TOnJsonRequest = reference to procedure(const AId: string; const AMethod: string; const AParams: string; var AResult: string; var AError: string);
  TOnClientCountChanged = reference to procedure(ACount: Integer);

  TJsonRpcServer = class(TComponent)
  private
    FTcp: TIdTCPServer;
    FOnRequest: TOnJsonRequest;
    FOnClientCountChanged: TOnClientCountChanged;
    FToken: string;
    procedure DoExecute(AContext: TIdContext);
    procedure DoConnect(AContext: TIdContext);
    procedure DoDisconnect(AContext: TIdContext);
  public
    constructor Create(AOwner: TComponent); override;
    destructor Destroy; override;
    procedure Start(Host: string; Port: Integer; const Token: string = '');
    procedure Stop;
    procedure Notify(const AMethod, AParamsJson: string);
    property OnRequest: TOnJsonRequest read FOnRequest write FOnRequest;
    property OnClientCountChanged: TOnClientCountChanged read FOnClientCountChanged write FOnClientCountChanged;
  end;

implementation

uses
  System.JSON;

constructor TJsonRpcServer.Create(AOwner: TComponent);
begin
  inherited;
  FTcp := TIdTCPServer.Create(Self);
  FTcp.OnExecute := DoExecute;
  FTcp.OnConnect := DoConnect;
  FTcp.OnDisconnect := DoDisconnect;
end;

destructor TJsonRpcServer.Destroy;
begin
  Stop;
  inherited;
end;

procedure TJsonRpcServer.Start(Host: string; Port: Integer; const Token: string);
begin
  FToken := Token;
  FTcp.DefaultPort := Port;
  FTcp.Active := True;
end;

procedure TJsonRpcServer.Stop;
begin
  FTcp.Active := False;
end;

procedure TJsonRpcServer.Notify(const AMethod, AParamsJson: string);
var
  LObj: TJSONObject;
  LJson: string;
  LList: TList;
  I: Integer;
  Ctx: TIdContext;
begin
  LObj := TJSONObject.Create;
  try
    LObj.AddPair('jsonrpc', '2.0');
    LObj.AddPair('method', AMethod);
    if AParamsJson <> '' then
      LObj.AddPair('params', TJSONObject.ParseJSONValue(AParamsJson) as TJSONValue)
    else
      LObj.AddPair('params', TJSONObject.Create);
    LJson := LObj.ToJSON;
  finally
    LObj.Free;
  end;
  if FTcp.Active then
  begin
    LList := FTcp.Contexts.LockList;
    try
      for I := 0 to LList.Count - 1 do
      begin
        Ctx := TIdContext(LList[I]);
        try
          Ctx.Connection.IOHandler.WriteLn(LJson);
        except
          // ignore write errors
        end;
      end;
    finally
      FTcp.Contexts.UnlockList;
    end;
  end;
end;

procedure TJsonRpcServer.DoConnect(AContext: TIdContext);
begin
  if Assigned(FOnClientCountChanged) then
    FOnClientCountChanged(FTcp.Contexts.Count);
end;

procedure TJsonRpcServer.DoDisconnect(AContext: TIdContext);
begin
  if Assigned(FOnClientCountChanged) then
    FOnClientCountChanged(FTcp.Contexts.Count);
end;

procedure TJsonRpcServer.DoExecute(AContext: TIdContext);
var
  LLine: string;
  LJson, LResultObj: TJSONObject;
  LId, LMethod, LError, LParamsStr, LResultStr: string;
  LParams: TJSONValue;
  LToken: string;
begin
  LLine := AContext.Connection.IOHandler.ReadLn;
  if LLine = '' then Exit;
  LJson := TJSONObject.ParseJSONValue(LLine) as TJSONObject;
  try
    if LJson = nil then Exit;
    LId := LJson.GetValue<string>('id', '');
    LMethod := LJson.GetValue<string>('method', '');
    LParams := LJson.getValue('params');
    if Assigned(LParams) then LParamsStr := LParams.ToJSON else LParamsStr := '{}';

    if LMethod = 'auth/handshake' then
    begin
      LToken := TJSONObject.ParseJSONValue(LParamsStr).GetValue<string>('token', '');
      if (FToken <> '') and (LToken <> FToken) then
      begin
        LResultObj := TJSONObject.Create;
        try
          LResultObj.AddPair('jsonrpc', '2.0');
          LResultObj.AddPair('id', LId);
          LResultObj.AddPair('error', TJSONObject.Create.AddPair('code', -32000).AddPair('message', 'unauthorized'));
          AContext.Connection.IOHandler.WriteLn(LResultObj.ToJSON);
        finally
          LResultObj.Free;
        end;
        Exit;
      end;
      Exit; // no response for notification
    end;

    if Assigned(FOnRequest) then
      FOnRequest(LId, LMethod, LParamsStr, LResultStr, LError)
    else
      LError := 'not implemented';

    LResultObj := TJSONObject.Create;
    try
      LResultObj.AddPair('jsonrpc', '2.0');
      if LId <> '' then LResultObj.AddPair('id', LId);
      if LError <> '' then
        LResultObj.AddPair('error', TJSONObject.Create.AddPair('code', -32603).AddPair('message', LError))
      else
        LResultObj.AddPair('result', TJSONObject.ParseJSONValue(LResultStr) as TJSONValue);
      AContext.Connection.IOHandler.WriteLn(LResultObj.ToJSON);
    finally
      LResultObj.Free;
    end;
  finally
    LJson.Free;
  end;
end;

end.