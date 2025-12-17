import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { nome, email, telefone, oab, areas, cidades } = body;

    // Validate required fields
    if (!nome || !email || !oab) {
      return NextResponse.json(
        { error: 'Campos obrigatórios faltando' },
        { status: 400 }
      );
    }

    // TODO: Integrate with your CRM or database
    // Example: Save to database, send to email, or webhook
    console.log('New lead received:', {
      nome,
      email,
      telefone,
      oab,
      areas,
      cidades,
      timestamp: new Date().toISOString()
    });

    // TODO: Send confirmation email to user
    // TODO: Send notification to admin

    // Mock successful response
    return NextResponse.json(
      {
        success: true,
        message: 'Lead cadastrado com sucesso'
      },
      { status: 200 }
    );
  } catch (error) {
    console.error('Error processing lead:', error);
    return NextResponse.json(
      { error: 'Erro ao processar lead' },
      { status: 500 }
    );
  }
}
